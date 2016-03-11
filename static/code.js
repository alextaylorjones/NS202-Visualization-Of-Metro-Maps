//var cy;
//var cydata;
//var intercitation;

var DEFAULT_SAMPLES = "5000";
var DEFAULT_ALGO = "intercitation";

var clicked_nodes = [];

function getBaseUrl() {
    var re = new RegExp(/^.*\//);
    return re.exec(window.location.href);
}

function clearGraph(cy) {
    clicked_nodes = [];
    if (cy != null) {
        cy.destroy();
    }

}

function createCytoscapeGraph(graph) {
    var cy = createNewVis(graph);
    bindEvents(cy);
    return cy;
}

function getFullGraph(callback) {
    getGraph(DEFAULT_SAMPLES, callback);
}

function getGraph(samples, callback) {
    $.ajax({
        url: getBaseUrl() + '_get_cy_data/' + samples,
        dataType: 'json',
        async: true,
        success: function (data) {
            console.log("received full graph");
            console.log(data)
            //cydata = data;
            data.nodes.forEach(function (n) {
                n.grabbable = true;
                n.locked = false;
            });

            callback(data);
        }
    });
}

function getIntercitationGraph(src, dst, algo, callback) {
    $.ajax({
        url: getBaseUrl() + '_get_intercitation/' + src + "/" + dst + "/" + algo,
        dataType: 'json',
        async: true,
        success: function (data) {
            console.log("received intercitation data");
            console.log(data);

            data.nodes.forEach(function(n) {
                var c = Math.floor(n.data.coverage * 6) + 3;
                n.style = {
                    backgroundColor: "#3" + c + "3"
                };
                n.grabbable = false;
                n.locked = false;
            });
            callback(data);
        },
        error: function (xhr, string, error) {
            console.log("error...");
            grapher.update()
        }
    });
}


var grapher = {
    cy: null,
    reset: function () {
        console.log("called reset");

        $("#cs-loader").fadeIn();
        $("#cy").fadeOut();
        clearGraph(this.cy);

        $("#algorithmOpt").val(DEFAULT_ALGO);

        getFullGraph(function (data) {
            this.cy = createCytoscapeGraph(data);

            $("#cs-loader").fadeOut();
            $("#cy").fadeIn();

            this.cy.fit(200)
        });
    },
    drawIntercitation: function (src, dst) {
        console.log("called intercitation");

        $("#cs-loader").fadeIn();
        $("#cy").fadeOut();
        clearGraph(this.cy);

        var algo = $("#algorithmOpt").val();

        getIntercitationGraph(src, dst, algo, function (data) {
            this.cy = createCytoscapeGraph(data);


            $("#cs-loader").fadeOut();
            $("#cy").fadeIn();
            this.cy.fit(200)
        });
    },
    update: function () {
        console.log("called update");
        $("#cs-loader").fadeIn();
        $("#cy").fadeOut();
        clearGraph(this.cy);

        var samples = $("#samplesOpt").val();

        getGraph(samples, function (data) {
            this.cy = createCytoscapeGraph(data);
            $("#cs-loader").fadeOut();
            $("#cy").fadeIn();
            this.cy.fit(200)
        });

    }
};

function bindEvents(cy) {
    //partial pull from http://stackoverflow.com/questions/20993149/how-to-add-tooltip-on-mouseover-event-on-nodes-in-graph-with-cytoscape-js
    cy.on('mouseover', 'node', function (event) {
        var n = event.cyTarget;

        var g = "<b>" + n.data('title') + "</b>" + '<br>Authors: ' + n.data('authors') + '<br>Abstract:<br>' + n.data('abstract');

        document.getElementById("tooltip").innerHTML = g

    });

    cy.on('click', 'node', function (event) {
        var n = event.cyTarget;
        console.log('clicked node length: ' + clicked_nodes.length);

        if (clicked_nodes.length == 1 && $.inArray(n.data('id'), clicked_nodes) != -1) {
            cy.$('#' + n.data('id')).style('background-color', '#11479e');
            clicked_nodes = [];
            console.log("cleared background: " + n.data('id'))
        } else if (clicked_nodes.length == 1 && $.inArray(n.data('id'), clicked_nodes) == -1) {

            clicked_nodes.push(n.data('id'));
            console.log("intercitation for these nodes: " + clicked_nodes)

            grapher.drawIntercitation(clicked_nodes[0], clicked_nodes[1]);
            clicked_nodes = [];
        } else {
            clicked_nodes.push(n.data('id'));
            cy.$('#' + n.data('id')).style('background-color', '#9e4711');
            console.log("adding to clicked node: " + clicked_nodes)
        }
    });

    $('#config-toggle').on('click', function () {
        $('body').toggleClass('config-closed');

        cy.resize();
    });


}

function createNewVis(data) {
    return cytoscape({
        container: document.getElementById('cy'),
        boxSelectionEnabled: false,
        autounselectify: true,
        layout: {
            name: 'dagre'
        },
        style: [
            {
                selector: 'node',
                style: {
                    'content': 'data(id)',
                    'text-opacity': 0.5,
                    'text-valign': 'center',
                    'text-halign': 'right',
                    'background-color': '#11479e'
                }
            },

            {
                selector: 'edge',
                style: {
                    'width': 1,
                    'target-arrow-shape': 'triangle',
                    'line-color': '#9dbaea',
                    'target-arrow-color': '#9dbaea'
                }
            }
        ],

        elements: data
    });
}


$(function () { // on dom ready
    grapher.reset();
});
