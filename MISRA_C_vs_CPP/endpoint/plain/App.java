// One endpoint, plain Java: JDK HTTP server + JDBC over H2.
// GET /items[?author=X] with Authorization: Bearer <token>; POST /items.
import com.sun.net.httpserver.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.sql.*;
import java.util.regex.*;

public class App {
    static final String URL = "jdbc:h2:mem:app;DB_CLOSE_DELAY=-1";

    public static void main(String[] args) throws Exception {
        try (Connection c = DriverManager.getConnection(URL);
             Statement st = c.createStatement()) {
            st.execute(new String(Files.readAllBytes(Paths.get("schema.sql")),
                                  StandardCharsets.UTF_8));
        }
        int port = args.length > 0 ? Integer.parseInt(args[0]) : 8080;
        HttpServer s = HttpServer.create(new java.net.InetSocketAddress(port), 0);
        s.createContext("/items", App::items);
        s.start();
        System.out.println("ready on " + port);
    }

    static void items(HttpExchange x) throws IOException {
        try {
            String user = authed(x);
            if (user == null) { send(x, 401, "{\"error\":\"unauthorized\"}"); return; }
            if (x.getRequestMethod().equals("GET"))       list(x);
            else if (x.getRequestMethod().equals("POST")) add(x);
            else send(x, 405, "{\"error\":\"method\"}");
        } catch (Exception e) {
            send(x, 500, "{\"error\":\"internal\"}");
        }
    }

    static String authed(HttpExchange x) throws SQLException {
        String h = x.getRequestHeaders().getFirst("Authorization");
        if (h == null || !h.startsWith("Bearer ")) return null;
        try (Connection c = DriverManager.getConnection(URL);
             PreparedStatement p = c.prepareStatement(
                 "SELECT username FROM tokens WHERE token = ?")) {
            p.setString(1, h.substring(7));
            ResultSet r = p.executeQuery();
            return r.next() ? r.getString(1) : null;
        }
    }

    static void list(HttpExchange x) throws SQLException, IOException {
        String q = x.getRequestURI().getQuery();
        String author = null;
        if (q != null)
            for (String kv : q.split("&"))
                if (kv.startsWith("author=")) author = kv.substring(7);
        String sql = author == null
            ? "SELECT id, author, name FROM items ORDER BY id"
            : "SELECT id, author, name FROM items WHERE author = ? ORDER BY id";
        try (Connection c = DriverManager.getConnection(URL);
             PreparedStatement p = c.prepareStatement(sql)) {
            if (author != null) p.setString(1, author);
            ResultSet r = p.executeQuery();
            StringBuilder b = new StringBuilder("[");
            while (r.next()) {
                if (b.length() > 1) b.append(",");
                b.append("{\"id\":").append(r.getLong(1))
                 .append(",\"author\":\"").append(r.getString(2))
                 .append("\",\"name\":\"").append(r.getString(3)).append("\"}");
            }
            send(x, 200, b.append("]").toString());
        }
    }

    static void add(HttpExchange x) throws SQLException, IOException {
        String body = new String(x.getRequestBody().readAllBytes(),
                                 StandardCharsets.UTF_8);
        String author = field(body, "author"), name = field(body, "name");
        if (author == null || name == null) {
            send(x, 400, "{\"error\":\"bad_request\"}");
            return;
        }
        try (Connection c = DriverManager.getConnection(URL);
             PreparedStatement p = c.prepareStatement(
                 "INSERT INTO items(author, name) VALUES(?, ?)",
                 Statement.RETURN_GENERATED_KEYS)) {
            p.setString(1, author);
            p.setString(2, name);
            p.executeUpdate();
            ResultSet k = p.getGeneratedKeys();
            k.next();
            send(x, 201, "{\"id\":" + k.getLong(1) + "}");
        }
    }

    static String field(String json, String name) {
        Matcher m = Pattern.compile("\"" + name + "\"\\s*:\\s*\"([^\"]*)\"")
                           .matcher(json);
        return m.find() ? m.group(1) : null;
    }

    static void send(HttpExchange x, int code, String body) throws IOException {
        byte[] b = body.getBytes(StandardCharsets.UTF_8);
        x.getResponseHeaders().set("Content-Type", "application/json");
        x.sendResponseHeaders(code, b.length);
        x.getResponseBody().write(b);
        x.close();
    }
}
