#!/usr/bin/env python3
"""gen.py: the six C/C++ pairs of the registered design.

One construct per pair, same behavior on both sides, checked by the hidden
suite before any task is given:

  virt  direct call vs virtual override in a registry
  tmpl  duplicated typed loops vs one template in a header
  oper  named functions vs operator overloads
  raii  explicit open/close and free on every path vs constructor/destructor
  inh   struct embedding with delegation vs inheritance
  mix   the constructs together at systems rates (interface with two
        overrides, one template helper, unique_ptr, one operator<)

build(pair, lang) -> {filename: content}. Every program reads a plain
data.txt of id|value lines in the working directory; behavior is
deterministic, no time and no randomness.
"""

MK_C = "store: $(SRC)\n\tcc -std=c99 -Wall -Werror -o store $(SRC)\n"
MK_CPP = "store: $(SRC)\n\tc++ -std=c++17 -Wall -Werror -o store $(SRC)\n"


def mk(lang, srcs):
    tpl = MK_C if lang == "c" else MK_CPP
    return "SRC = " + " ".join(srcs) + "\n" + tpl

README = """# store

A small record tool. Records live in ./data.txt, one per line, as id|value.

Build and try:

    make
    ./store {cmds}

The program must build with `make` and keep its current commands working.
"""

# ---------------------------------------------------------------- virt ----
VIRT_C = {"store.c": r"""
/* store: id|value records in data.txt. Commands: add, list, find, count. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static FILE *open_data(const char *mode)
{
    FILE *f = fopen("data.txt", mode);
    if (f == NULL && mode[0] == 'r')
        f = fopen("/dev/null", "r");
    return f;
}

static int cmd_add(int argc, char **argv)
{
    FILE *f;
    if (argc < 2) { fprintf(stderr, "add ID VALUE\n"); return 2; }
    f = open_data("a");
    if (f == NULL) return 1;
    fprintf(f, "%s|%s\n", argv[0], argv[1]);
    fclose(f);
    return 0;
}

static int cmd_list(int argc, char **argv)
{
    char line[512];
    FILE *f = open_data("r");
    (void)argc; (void)argv;
    if (f == NULL) return 1;
    while (fgets(line, sizeof line, f) != NULL)
        fputs(line, stdout);
    fclose(f);
    return 0;
}

static int cmd_find(int argc, char **argv)
{
    char line[512];
    FILE *f;
    if (argc < 1) { fprintf(stderr, "find NEEDLE\n"); return 2; }
    f = open_data("r");
    if (f == NULL) return 1;
    while (fgets(line, sizeof line, f) != NULL)
        if (strstr(line, argv[0]) != NULL)
            fputs(line, stdout);
    fclose(f);
    return 0;
}

static int cmd_count(int argc, char **argv)
{
    char line[512];
    long n = 0;
    FILE *f = open_data("r");
    (void)argc; (void)argv;
    if (f == NULL) return 1;
    while (fgets(line, sizeof line, f) != NULL)
        n++;
    fclose(f);
    printf("%ld\n", n);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "store CMD [ARGS]\n"); return 2; }
    if (strcmp(argv[1], "add") == 0)   return cmd_add(argc - 2, argv + 2);
    if (strcmp(argv[1], "list") == 0)  return cmd_list(argc - 2, argv + 2);
    if (strcmp(argv[1], "find") == 0)  return cmd_find(argc - 2, argv + 2);
    if (strcmp(argv[1], "count") == 0) return cmd_count(argc - 2, argv + 2);
    fprintf(stderr, "unknown command: %s\n", argv[1]);
    return 2;
}
"""}

VIRT_CPP = {
"command.h": r"""
// One command of the store: name() keys the registry, run() does the work.
#pragma once
#include <string>
#include <vector>

class Command {
public:
    virtual ~Command() = default;
    virtual std::string name() const = 0;
    virtual int run(const std::vector<std::string>& args) = 0;
};
""",
"store_io.h": r"""
#pragma once
#include <string>
#include <vector>
std::vector<std::string> read_lines();
bool append_line(const std::string& line);
""",
"store_io.cpp": r"""
#include "store_io.h"
#include <fstream>

std::vector<std::string> read_lines()
{
    std::vector<std::string> out;
    std::ifstream f("data.txt");
    std::string line;
    while (std::getline(f, line))
        out.push_back(line);
    return out;
}

bool append_line(const std::string& line)
{
    std::ofstream f("data.txt", std::ios::app);
    if (!f)
        return false;
    f << line << "\n";
    return true;
}
""",
"cmd_add.cpp": r"""
#include "command.h"
#include "store_io.h"
#include <cstdio>

class CmdAdd : public Command {
public:
    std::string name() const override { return "add"; }
    int run(const std::vector<std::string>& args) override
    {
        if (args.size() < 2) { std::fprintf(stderr, "add ID VALUE\n"); return 2; }
        return append_line(args[0] + "|" + args[1]) ? 0 : 1;
    }
};
Command* make_add() { return new CmdAdd; }
""",
"cmd_list.cpp": r"""
#include "command.h"
#include "store_io.h"
#include <cstdio>

class CmdList : public Command {
public:
    std::string name() const override { return "list"; }
    int run(const std::vector<std::string>&) override
    {
        for (const auto& line : read_lines())
            std::printf("%s\n", line.c_str());
        return 0;
    }
};
Command* make_list() { return new CmdList; }
""",
"cmd_find.cpp": r"""
#include "command.h"
#include "store_io.h"
#include <cstdio>

class CmdFind : public Command {
public:
    std::string name() const override { return "find"; }
    int run(const std::vector<std::string>& args) override
    {
        if (args.empty()) { std::fprintf(stderr, "find NEEDLE\n"); return 2; }
        for (const auto& line : read_lines())
            if (line.find(args[0]) != std::string::npos)
                std::printf("%s\n", line.c_str());
        return 0;
    }
};
Command* make_find() { return new CmdFind; }
""",
"cmd_count.cpp": r"""
#include "command.h"
#include "store_io.h"
#include <cstdio>

class CmdCount : public Command {
public:
    std::string name() const override { return "count"; }
    int run(const std::vector<std::string>&) override
    {
        std::printf("%zu\n", read_lines().size());
        return 0;
    }
};
Command* make_count() { return new CmdCount; }
""",
"main.cpp": r"""
#include "command.h"
#include <cstdio>
#include <memory>

Command* make_add();
Command* make_list();
Command* make_find();
Command* make_count();

int main(int argc, char **argv)
{
    std::vector<std::unique_ptr<Command>> cmds;
    cmds.emplace_back(make_add());
    cmds.emplace_back(make_list());
    cmds.emplace_back(make_find());
    cmds.emplace_back(make_count());
    if (argc < 2) { std::fprintf(stderr, "store CMD [ARGS]\n"); return 2; }
    std::vector<std::string> args(argv + 2, argv + argc);
    for (auto& c : cmds)
        if (c->name() == argv[1])
            return c->run(args);
    std::fprintf(stderr, "unknown command: %s\n", argv[1]);
    return 2;
}
"""}

# ---------------------------------------------------------------- tmpl ----
TMPL_C = {"store.c": r"""
/* store: id|value records in data.txt. Commands: maxid, longest. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 4096

static long ids[MAXN];
static char values[MAXN][256];
static int nrec;

static void load(void)
{
    char line[512];
    FILE *f = fopen("data.txt", "r");
    if (f == NULL)
        return;
    while (nrec < MAXN && fgets(line, sizeof line, f) != NULL) {
        char *bar = strchr(line, '|');
        size_t n;
        if (bar == NULL)
            continue;
        *bar = '\0';
        ids[nrec] = strtol(line, NULL, 10);
        n = strcspn(bar + 1, "\n");
        if (n > 255) n = 255;
        memcpy(values[nrec], bar + 1, n);
        values[nrec][n] = '\0';
        nrec++;
    }
    fclose(f);
}

/* The record with the numerically largest id; first wins a tie. */
static int best_by_id(void)
{
    int best = 0, i;
    for (i = 1; i < nrec; i++)
        if (ids[i] > ids[best])
            best = i;
    return best;
}

/* The record with the longest value; first wins a tie. */
static int best_by_len(void)
{
    int best = 0, i;
    for (i = 1; i < nrec; i++)
        if (strlen(values[i]) > strlen(values[best]))
            best = i;
    return best;
}

int main(int argc, char **argv)
{
    int b;
    if (argc < 2) { fprintf(stderr, "store maxid|longest\n"); return 2; }
    load();
    if (nrec == 0) { printf("empty\n"); return 1; }
    if (strcmp(argv[1], "maxid") == 0)
        b = best_by_id();
    else if (strcmp(argv[1], "longest") == 0)
        b = best_by_len();
    else { fprintf(stderr, "unknown command: %s\n", argv[1]); return 2; }
    printf("%ld|%s\n", ids[b], values[b]);
    return 0;
}
"""}

TMPL_CPP = {
"maxby.h": r"""
// The index of the record whose key is largest; the first wins a tie.
#pragma once
#include <cstddef>
#include <vector>

template <typename Key, typename F>
std::size_t max_by(std::size_t n, F key)
{
    std::size_t best = 0;
    for (std::size_t i = 1; i < n; i++)
        if (key(i) > key(best))
            best = i;
    return best;
}
""",
"main.cpp": r"""
#include "maxby.h"
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

static std::vector<long> ids;
static std::vector<std::string> values;

static void load()
{
    std::ifstream f("data.txt");
    std::string line;
    while (std::getline(f, line)) {
        auto bar = line.find('|');
        if (bar == std::string::npos)
            continue;
        ids.push_back(std::stol(line.substr(0, bar)));
        values.push_back(line.substr(bar + 1));
    }
}

int main(int argc, char **argv)
{
    std::size_t b;
    if (argc < 2) { std::fprintf(stderr, "store maxid|longest\n"); return 2; }
    load();
    if (ids.empty()) { std::printf("empty\n"); return 1; }
    if (std::strcmp(argv[1], "maxid") == 0)
        b = max_by<long>(ids.size(), [](std::size_t i) { return ids[i]; });
    else if (std::strcmp(argv[1], "longest") == 0)
        b = max_by<std::size_t>(ids.size(),
                                [](std::size_t i) { return values[i].size(); });
    else { std::fprintf(stderr, "unknown command: %s\n", argv[1]); return 2; }
    std::printf("%ld|%s\n", ids[b], values[b].c_str());
    return 0;
}
"""}

# ---------------------------------------------------------------- oper ----
OPER_C = {"store.c": r"""
/* store: label|cents amounts in data.txt. Commands: sum, max. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct money { long cents; };

static struct money money_add(struct money a, struct money b)
{
    struct money r;
    r.cents = a.cents + b.cents;
    return r;
}

static int money_less(struct money a, struct money b)
{
    return a.cents < b.cents;
}

static void money_print(struct money m)
{
    long c = m.cents < 0 ? -m.cents : m.cents;
    printf("%s%ld.%02ld\n", m.cents < 0 ? "-" : "", c / 100, c % 100);
}

int main(int argc, char **argv)
{
    char line[512];
    struct money total = {0}, best = {0};
    int seen = 0;
    FILE *f;
    if (argc < 2) { fprintf(stderr, "store sum|max\n"); return 2; }
    f = fopen("data.txt", "r");
    if (f == NULL) { printf("empty\n"); return 1; }
    while (fgets(line, sizeof line, f) != NULL) {
        char *bar = strchr(line, '|');
        struct money m;
        if (bar == NULL)
            continue;
        m.cents = strtol(bar + 1, NULL, 10);
        total = money_add(total, m);
        if (!seen || money_less(best, m))
            best = m;
        seen = 1;
    }
    fclose(f);
    if (!seen) { printf("empty\n"); return 1; }
    if (strcmp(argv[1], "sum") == 0)
        money_print(total);
    else if (strcmp(argv[1], "max") == 0)
        money_print(best);
    else { fprintf(stderr, "unknown command: %s\n", argv[1]); return 2; }
    return 0;
}
"""}

OPER_CPP = {
"money.h": r"""
// An amount in cents; printing renders dollars.cents with the sign.
#pragma once
#include <ostream>

struct Money {
    long cents = 0;
};

inline Money operator+(Money a, Money b) { return Money{a.cents + b.cents}; }
inline bool operator<(Money a, Money b) { return a.cents < b.cents; }

inline std::ostream& operator<<(std::ostream& os, Money m)
{
    long c = m.cents < 0 ? -m.cents : m.cents;
    if (m.cents < 0)
        os << '-';
    char buf[8];
    std::snprintf(buf, sizeof buf, "%02ld", c % 100);
    return os << c / 100 << '.' << buf;
}
""",
"main.cpp": r"""
#include "money.h"
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>

int main(int argc, char **argv)
{
    Money total, best;
    bool seen = false;
    if (argc < 2) { std::fprintf(stderr, "store sum|max\n"); return 2; }
    std::ifstream f("data.txt");
    if (!f) { std::cout << "empty\n"; return 1; }
    std::string line;
    while (std::getline(f, line)) {
        auto bar = line.find('|');
        if (bar == std::string::npos)
            continue;
        Money m{std::stol(line.substr(bar + 1))};
        total = total + m;
        if (!seen || best < m)
            best = m;
        seen = true;
    }
    if (!seen) { std::cout << "empty\n"; return 1; }
    if (std::strcmp(argv[1], "sum") == 0)
        std::cout << total << "\n";
    else if (std::strcmp(argv[1], "max") == 0)
        std::cout << best << "\n";
    else { std::fprintf(stderr, "unknown command: %s\n", argv[1]); return 2; }
    return 0;
}
"""}

# ---------------------------------------------------------------- raii ----
RAII_C = {"store.c": r"""
/* store: pack MINLEN -- copy records with value length >= MINLEN from
 * data.txt to out.txt, then a trailer line "packed K". */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv)
{
    FILE *in = NULL, *out = NULL;
    char *buf = NULL;
    long minlen, k = 0;
    if (argc < 3 || strcmp(argv[1], "pack") != 0) {
        fprintf(stderr, "store pack MINLEN\n");
        return 2;
    }
    minlen = strtol(argv[2], NULL, 10);
    in = fopen("data.txt", "r");
    if (in == NULL) {
        fprintf(stderr, "no data.txt\n");
        return 1;
    }
    out = fopen("out.txt", "w");
    if (out == NULL) {
        fclose(in);
        return 1;
    }
    buf = malloc(512);
    if (buf == NULL) {
        fclose(in);
        fclose(out);
        return 1;
    }
    while (fgets(buf, 512, in) != NULL) {
        char *bar = strchr(buf, '|');
        if (bar == NULL)
            continue;
        if ((long)strcspn(bar + 1, "\n") >= minlen) {
            fputs(buf, out);
            k++;
        }
    }
    fprintf(out, "packed %ld\n", k);
    free(buf);
    fclose(in);
    fclose(out);
    return 0;
}
"""}

RAII_CPP = {
"file.h": r"""
// A file that closes itself; open failure leaves it false.
#pragma once
#include <cstdio>
#include <string>

class File {
public:
    File(const char *path, const char *mode) : f_(std::fopen(path, mode)) {}
    ~File() { if (f_) std::fclose(f_); }
    File(const File&) = delete;
    File& operator=(const File&) = delete;
    explicit operator bool() const { return f_ != nullptr; }
    std::FILE *get() { return f_; }
private:
    std::FILE *f_;
};
""",
"main.cpp": r"""
#include "file.h"
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

int main(int argc, char **argv)
{
    if (argc < 3 || std::strcmp(argv[1], "pack") != 0) {
        std::fprintf(stderr, "store pack MINLEN\n");
        return 2;
    }
    long minlen = std::strtol(argv[2], nullptr, 10), k = 0;
    File in("data.txt", "r");
    if (!in) {
        std::fprintf(stderr, "no data.txt\n");
        return 1;
    }
    File out("out.txt", "w");
    if (!out)
        return 1;
    std::vector<char> buf(512);
    while (std::fgets(buf.data(), 512, in.get()) != nullptr) {
        char *bar = std::strchr(buf.data(), '|');
        if (bar == nullptr)
            continue;
        if ((long)std::strcspn(bar + 1, "\n") >= minlen) {
            std::fputs(buf.data(), out.get());
            k++;
        }
    }
    std::fprintf(out.get(), "packed %ld\n", k);
    return 0;
}
"""}

# ----------------------------------------------------------------- inh ----
INH_C = {"store.c": r"""
/* store: plain records "id|value" and extended "E|id|value|who".
 * Commands: list (normalized), who (each distinct who, in order). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct rec { long id; char value[256]; };
struct erec { struct rec base; char who[64]; };

static void rec_print(const struct rec *r)
{
    printf("%ld|%s\n", r->id, r->value);
}

static void erec_print(const struct erec *e)
{
    printf("%ld|%s|%s\n", e->base.id, e->base.value, e->who);
}

static char whos[64][64];
static int nwho;

static void who_seen(const char *w)
{
    int i;
    for (i = 0; i < nwho; i++)
        if (strcmp(whos[i], w) == 0)
            return;
    if (nwho < 64)
        snprintf(whos[nwho++], 64, "%s", w);
}

static void field(char *dst, size_t sz, const char *src, size_t n)
{
    if (n >= sz) n = sz - 1;
    memcpy(dst, src, n);
    dst[n] = '\0';
}

int main(int argc, char **argv)
{
    char line[512];
    int do_who;
    FILE *f;
    if (argc < 2) { fprintf(stderr, "store list|who\n"); return 2; }
    do_who = strcmp(argv[1], "who") == 0;
    if (!do_who && strcmp(argv[1], "list") != 0) {
        fprintf(stderr, "unknown command: %s\n", argv[1]);
        return 2;
    }
    f = fopen("data.txt", "r");
    if (f == NULL)
        return 1;
    while (fgets(line, sizeof line, f) != NULL) {
        char *p1, *p2, *p3;
        line[strcspn(line, "\n")] = '\0';
        if (strncmp(line, "E|", 2) == 0) {
            struct erec e;
            p1 = line + 2;
            p2 = strchr(p1, '|');
            if (p2 == NULL) continue;
            p3 = strchr(p2 + 1, '|');
            if (p3 == NULL) continue;
            e.base.id = strtol(p1, NULL, 10);
            field(e.base.value, sizeof e.base.value, p2 + 1, (size_t)(p3 - p2 - 1));
            field(e.who, sizeof e.who, p3 + 1, strlen(p3 + 1));
            if (do_who)
                who_seen(e.who);
            else
                erec_print(&e);
        } else {
            struct rec r;
            p1 = strchr(line, '|');
            if (p1 == NULL) continue;
            r.id = strtol(line, NULL, 10);
            field(r.value, sizeof r.value, p1 + 1, strlen(p1 + 1));
            if (!do_who)
                rec_print(&r);
        }
    }
    fclose(f);
    if (do_who) {
        int i;
        for (i = 0; i < nwho; i++)
            printf("%s\n", whos[i]);
    }
    return 0;
}
"""}

INH_CPP = {
"rec.h": r"""
// A record; ERec extends it with the person it belongs to.
#pragma once
#include <cstdio>
#include <string>

class Rec {
public:
    Rec(long id, std::string value) : id_(id), value_(std::move(value)) {}
    virtual ~Rec() = default;
    virtual void print() const { std::printf("%ld|%s\n", id_, value_.c_str()); }
    long id() const { return id_; }
    const std::string& value() const { return value_; }
private:
    long id_;
    std::string value_;
};

class ERec : public Rec {
public:
    ERec(long id, std::string value, std::string who)
        : Rec(id, std::move(value)), who_(std::move(who)) {}
    void print() const override
    {
        std::printf("%ld|%s|%s\n", id(), value().c_str(), who_.c_str());
    }
    const std::string& who() const { return who_; }
private:
    std::string who_;
};
""",
"main.cpp": r"""
#include "rec.h"
#include <cstring>
#include <fstream>
#include <memory>
#include <vector>

static std::vector<std::unique_ptr<Rec>> load()
{
    std::vector<std::unique_ptr<Rec>> out;
    std::ifstream f("data.txt");
    std::string line;
    while (std::getline(f, line)) {
        if (line.rfind("E|", 0) == 0) {
            auto p2 = line.find('|', 2);
            if (p2 == std::string::npos) continue;
            auto p3 = line.find('|', p2 + 1);
            if (p3 == std::string::npos) continue;
            out.push_back(std::make_unique<ERec>(
                std::stol(line.substr(2, p2 - 2)),
                line.substr(p2 + 1, p3 - p2 - 1), line.substr(p3 + 1)));
        } else {
            auto p1 = line.find('|');
            if (p1 == std::string::npos) continue;
            out.push_back(std::make_unique<Rec>(std::stol(line.substr(0, p1)),
                                                line.substr(p1 + 1)));
        }
    }
    return out;
}

int main(int argc, char **argv)
{
    if (argc < 2) { std::fprintf(stderr, "store list|who\n"); return 2; }
    auto recs = load();
    if (std::strcmp(argv[1], "list") == 0) {
        for (const auto& r : recs)
            r->print();
        return 0;
    }
    if (std::strcmp(argv[1], "who") == 0) {
        std::vector<std::string> seen;
        for (const auto& r : recs)
            if (auto *e = dynamic_cast<const ERec*>(r.get())) {
                bool dup = false;
                for (const auto& w : seen)
                    if (w == e->who())
                        dup = true;
                if (!dup)
                    seen.push_back(e->who());
            }
        for (const auto& w : seen)
            std::printf("%s\n", w.c_str());
        return 0;
    }
    std::fprintf(stderr, "unknown command: %s\n", argv[1]);
    return 2;
}
"""}

# ----------------------------------------------------------------- mix ----
MIX_C = {"store.c": r"""
/* store: report MINLEN [FILE|-] -- records with value length >= MINLEN,
 * sorted by id ascending (input order on ties), one id|value per line.
 * FILE default data.txt; "-" reads stdin. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct rec { long id; char value[256]; int seq; };

static struct rec recs[4096];
static int nrec;

static void load(FILE *f)
{
    char line[512];
    while (nrec < 4096 && fgets(line, sizeof line, f) != NULL) {
        char *bar = strchr(line, '|');
        size_t n;
        if (bar == NULL)
            continue;
        recs[nrec].id = strtol(line, NULL, 10);
        n = strcspn(bar + 1, "\n");
        if (n > 255) n = 255;
        memcpy(recs[nrec].value, bar + 1, n);
        recs[nrec].value[n] = '\0';
        recs[nrec].seq = nrec;
        nrec++;
    }
}

static int by_id(const void *a, const void *b)
{
    const struct rec *ra = a, *rb = b;
    if (ra->id != rb->id)
        return ra->id < rb->id ? -1 : 1;
    return ra->seq - rb->seq;
}

int main(int argc, char **argv)
{
    long minlen;
    int i;
    FILE *f;
    if (argc < 3 || strcmp(argv[1], "report") != 0) {
        fprintf(stderr, "store report MINLEN [FILE|-]\n");
        return 2;
    }
    minlen = strtol(argv[2], NULL, 10);
    if (argc > 3 && strcmp(argv[3], "-") == 0)
        f = stdin;
    else
        f = fopen(argc > 3 ? argv[3] : "data.txt", "r");
    if (f == NULL) {
        fprintf(stderr, "cannot open input\n");
        return 1;
    }
    load(f);
    if (f != stdin)
        fclose(f);
    qsort(recs, nrec, sizeof recs[0], by_id);
    for (i = 0; i < nrec; i++)
        if ((long)strlen(recs[i].value) >= minlen)
            printf("%ld|%s\n", recs[i].id, recs[i].value);
    return 0;
}
"""}

MIX_CPP = {
"reader.h": r"""
// Where records come from: a named file, or standard input for "-".
#pragma once
#include <memory>
#include <string>
#include <vector>

struct Record {
    long id;
    std::string value;
    int seq;
};

inline bool operator<(const Record& a, const Record& b)
{
    if (a.id != b.id)
        return a.id < b.id;
    return a.seq < b.seq;
}

class Reader {
public:
    virtual ~Reader() = default;
    virtual std::vector<Record> read() = 0;
};

std::unique_ptr<Reader> make_reader(const std::string& spec);
""",
"reader.cpp": r"""
#include "reader.h"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>

namespace {

std::vector<Record> parse(std::istream& in)
{
    std::vector<Record> out;
    std::string line;
    int seq = 0;
    while (std::getline(in, line)) {
        auto bar = line.find('|');
        if (bar == std::string::npos)
            continue;
        out.push_back({std::stol(line.substr(0, bar)), line.substr(bar + 1), seq++});
    }
    return out;
}

class FileReader : public Reader {
public:
    explicit FileReader(std::string path) : path_(std::move(path)) {}
    std::vector<Record> read() override
    {
        std::ifstream f(path_);
        if (!f) {
            std::fprintf(stderr, "cannot open input\n");
            std::exit(1);
        }
        return parse(f);
    }
private:
    std::string path_;
};

class StdinReader : public Reader {
public:
    std::vector<Record> read() override { return parse(std::cin); }
};

} // namespace

std::unique_ptr<Reader> make_reader(const std::string& spec)
{
    if (spec == "-")
        return std::make_unique<StdinReader>();
    return std::make_unique<FileReader>(spec);
}
""",
"keep.h": r"""
// Keep the elements the predicate admits, preserving order.
#pragma once
#include <vector>

template <typename T, typename P>
std::vector<T> keep(const std::vector<T>& in, P pred)
{
    std::vector<T> out;
    for (const auto& x : in)
        if (pred(x))
            out.push_back(x);
    return out;
}
""",
"main.cpp": r"""
#include "keep.h"
#include "reader.h"
#include <algorithm>
#include <cstdio>
#include <cstring>

int main(int argc, char **argv)
{
    if (argc < 3 || std::strcmp(argv[1], "report") != 0) {
        std::fprintf(stderr, "store report MINLEN [FILE|-]\n");
        return 2;
    }
    long minlen = std::strtol(argv[2], nullptr, 10);
    auto reader = make_reader(argc > 3 ? argv[3] : "data.txt");
    auto recs = reader->read();
    std::sort(recs.begin(), recs.end());
    auto kept = keep(recs, [minlen](const Record& r) {
        return (long)r.value.size() >= minlen;
    });
    for (const auto& r : kept)
        std::printf("%ld|%s\n", r.id, r.value.c_str());
    return 0;
}
"""}

PAIRS = {
    "virt": {"c": VIRT_C, "cpp": VIRT_CPP, "cmds": "add 7 tea && ./store list"},
    "tmpl": {"c": TMPL_C, "cpp": TMPL_CPP, "cmds": "maxid"},
    "oper": {"c": OPER_C, "cpp": OPER_CPP, "cmds": "sum"},
    "raii": {"c": RAII_C, "cpp": RAII_CPP, "cmds": "pack 3 && cat out.txt"},
    "inh":  {"c": INH_C, "cpp": INH_CPP, "cmds": "list"},
    "mix":  {"c": MIX_C, "cpp": MIX_CPP, "cmds": "report 3"},
}


def build(pair, lang):
    src = dict(PAIRS[pair][lang])
    names = sorted(src)
    files = dict(src)
    files["Makefile"] = mk(lang, [n for n in names if n.endswith((".c", ".cpp"))])
    files["README.md"] = README.format(cmds=PAIRS[pair]["cmds"])
    return files


if __name__ == "__main__":
    import sys, os
    pair, lang, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    for name, content in build(pair, lang).items():
        open(os.path.join(out, name), "w").write(content)
