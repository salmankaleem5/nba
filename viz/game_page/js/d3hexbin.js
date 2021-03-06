!function (n, t) {
    "object" == typeof exports && "undefined" != typeof module ? t(exports) : "function" == typeof define && define.amd ? define(["exports"], t) : t(n.d3_hexbin = n.d3_hexbin || {})
}(this, function (n) {
    "use strict";

    function t(n) {
        return n[0]
    }

    function r(n) {
        return n[1]
    }

    function e() {
        function n(n) {
            var t, r = {}, e = [], u = n.length;
            for (t = 0; u > t; ++t) if (!isNaN(o = +d.call(null, i = n[t], t, n)) && !isNaN(c = +v.call(null, i, t, n))) {
                var i, o, c, h = Math.round(c /= f), s = Math.round(o = o / a - (1 & h) / 2), l = c - h;
                if (3 * Math.abs(l) > 1) {
                    var p = o - s, x = s + (s > o ? -1 : 1) / 2, M = h + (h > c ? -1 : 1), m = o - x, g = c - M;
                    p * p + l * l > m * m + g * g && (s = x + (1 & h ? 1 : -1) / 2, h = M)
                }
                var b = s + "-" + h, y = r[b];
                y ? y.push(i) : (e.push(y = r[b] = [i]), y.x = (s + (1 & h) / 2) * a, y.y = h * f)
            }
            return e
        }

        function e(n) {
            var t = 0, r = 0;
            return o.map(function (e) {
                var u = Math.sin(e) * n, i = -Math.cos(e) * n, o = u - t, a = i - r;
                return t = u, r = i, [o, a]
            })
        }

        var u, a, f, c = 0, h = 0, s = 1, l = 1, d = t, v = r;
        return n.hexagon = function (n) {
            return "m" + e(null == n ? u : +n).join("l") + "z"
        }, n.centers = function () {
            for (var n = [], t = Math.round(h / f), r = Math.round(c / a), e = t * f; l + u > e; e += f, ++t) for (var i = r * a + (1 & t) * a / 2; s + a / 2 > i; i += a) n.push([i, e]);
            return n
        }, n.mesh = function () {
            var t = e(u).slice(0, 4).join("l");
            return n.centers().map(function (n) {
                return "M" + n + "m" + t
            }).join("")
        }, n.x = function (t) {
            return arguments.length ? (d = t, n) : d
        }, n.y = function (t) {
            return arguments.length ? (v = t, n) : v
        }, n.radius = function (t) {
            return arguments.length ? (u = +t, a = 2 * u * Math.sin(i), f = 1.5 * u, n) : u
        }, n.extent = function (t) {
            return arguments.length ? (c = +t[0][0], h = +t[0][1], s = +t[1][0], l = +t[1][1], n) : [[c, h], [s, l]]
        }, n.radius(1)
    }

    var u = "0.2.0", i = Math.PI / 3, o = [0, i, 2 * i, 3 * i, 4 * i, 5 * i];
    n.version = u, n.hexbin = e
});