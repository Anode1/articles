// Items screen: fetch, filter, sort, select, delete.
(function () {
  "use strict";

  var items = [];
  var selected = {};
  var sort = { key: "id", dir: 1 };
  var filterText = "";
  var minLen = 0;

  function $(id) { return document.getElementById(id); }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;",
               '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function visible() {
    var q = filterText.toLowerCase();
    var rows = items.filter(function (it) {
      if (q && it.name.toLowerCase().indexOf(q) < 0
            && it.author.toLowerCase().indexOf(q) < 0) return false;
      return it.name.length >= minLen;
    });
    rows.sort(function (a, b) {
      var x = a[sort.key], y = b[sort.key];
      return (x < y ? -1 : x > y ? 1 : 0) * sort.dir;
    });
    return rows;
  }

  function render() {
    var rows = visible();

    $("count").textContent = rows.length + (rows.length === 1 ? " item" : " items");

    var n = rows.filter(function (it) { return selected[it.id]; }).length;
    $("selected").textContent = n ? n + " selected" : "";

    ["id", "name"].forEach(function (key) {
      var th = document.querySelector('[data-sort="' + key + '"]');
      th.textContent = key === "id" ? "ID" : "Name";
      if (sort.key === key) th.textContent += sort.dir > 0 ? " ▲" : " ▼";
    });

    if (!rows.length) {
      $("rows").innerHTML = '<div class="empty">No items found.</div>';
      return;
    }

    $("rows").innerHTML = rows.map(function (it) {
      return '<div class="item-row" data-id="' + escapeHtml(it.id) + '">' +
        '<input type="checkbox" class="select"' + (selected[it.id] ? " checked" : "") + ">" +
        "<span>" + escapeHtml(it.id) + "</span>" +
        '<span class="item-author">' + escapeHtml(it.author) + "</span>" +
        '<span class="item-name">' + escapeHtml(it.name) + "</span>" +
        '<span class="badge badge-' + escapeHtml(it.state) + '">' +
          escapeHtml(it.state) + "</span>" +
        '<button class="delete">Delete</button>' +
      "</div>";
    }).join("");
  }

  $("rows").addEventListener("click", function (e) {
    var row = e.target.closest(".item-row");
    if (!row) return;
    var id = row.getAttribute("data-id");
    if (e.target.classList.contains("delete")) {
      items = items.filter(function (it) { return String(it.id) !== id; });
      delete selected[id];
      render();
    } else if (e.target.classList.contains("select")) {
      if (selected[id]) delete selected[id]; else selected[id] = true;
      render();
    }
  });

  $("filter").addEventListener("input", function (e) {
    filterText = e.target.value;
    render();
  });

  $("minLen").addEventListener("input", function (e) {
    minLen = parseInt(e.target.value, 10) || 0;
    render();
  });

  document.querySelector(".header").addEventListener("click", function (e) {
    var key = e.target.getAttribute("data-sort");
    if (!key) return;
    if (sort.key === key) sort.dir = -sort.dir; else { sort.key = key; sort.dir = 1; }
    render();
  });

  fetch("items.json").then(function (r) { return r.json(); }).then(function (data) {
    items = data;
    render();
  });
})();
