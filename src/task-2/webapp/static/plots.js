window.onload = function () {
    navbar = document.getElementById("navbarstick");
    getNavbarOffset();
};
window.onresize = function () {
    getNavbarOffset();
    stickyNavbar();
};

window.onscroll = stickyNavbar;

// SCROLL-DOWN BUTTON: WELCOME SCREEN: INDEX.HTML

$(function () {
    $(".scroll-down").click(function () {
        $("html, body").animate({ scrollTop: $(".nav").offset().top }, "slow");
        return false;
    });
});

// STICKY NAVBAR

var navbar;
var navbarVisibleScroll;

function getNavbarOffset() {
    // if ($("body").hasClass("home")) {
        navbarVisibleScroll = document.getElementById("welcome").clientHeight;
    // }
}

function stickyNavbar() {
    // if ($("body").hasClass("home")) {
        if (window.scrollY >= navbarVisibleScroll) {
            navbar.classList.add("sticky");
        } else {
            navbar.classList.remove("sticky");
        }
    // }
}


// PLOTS

function plot(data) {
    let layout1 = {
        margin: {
            l: 15,
            t: 0,
            b: 0,
        },
    };

    Plotly.newPlot("plot-1", data["lang"], layout1, { responsive: true });

    let layout2 = {
        margin: {
            l: 125,
            b: 85,
            t: 15,
        },
    };
    Plotly.newPlot("plot-2", data["corr"], layout2, { responsive: true });

    let layout3 = {
        dragmode: "zoom",
        geo: {
            showland: true,
            landcolor: "#e2daed",
            countrycolor: "#d3d3d3",
            countrywidth: 1.5,
            subunitwidth: 1.5,
            subunitcolor: "#d3d3d3",
            showsubunits: true,
            showcountries: true,
            showframe: false,
            showocean: true,
            oceancolor: "#bcb5ff",
            showcoastlines: false,
        },
        margin: {
            l: 15,
            r: 0,
        },
        legend: {
            title: "Languages",
        },
    };
    Plotly.newPlot("plot-3", data["places"], layout3, { responsive: true });

    let layout4 = {
        barmode: "overlay",
        xaxis: {
            range: [0, 1000],
            title: 'Number of friends/followers',
        },
        yaxis: {
            title: "Count",
        },
        bargap: 0.05,
        margin: {
            t: 0
        }
    };
    Plotly.newPlot("plot-4", data["ff"], layout4, {responsive: true});

    let layout5 = {
        barmode: "overlay",
        xaxis: {
            range: [0, 10000],
            title: "Number of tweets/likes given",
        },
        yaxis: {
            title: "Count",
        },
        bargap: 0.05,
        margin: {
            t: 0,
        },
    };
    Plotly.newPlot("plot-5", data["act"], layout5, { responsive: true });
}
