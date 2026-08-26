package demo;

import jakarta.persistence.*;

@Entity
@Table(name = "tokens")
public class Token {
    @Id
    private String token;
    private String username;

    public String getToken() { return token; }
    public String getUsername() { return username; }
}
