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

function getFullGraph(cb) {
    getGraph(DEFAULT_SAMPLES, DEFAULT_ALGO, cb);
}

function getGraph(samples, algo, cb) {
    $.ajax({
        url: getBaseUrl() + '_get_cy_data/' + samples + "/" + algo,
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

            cb(data);
        }
    });
}

function getIntercitationGraph(src, dst, cb) {
    $.ajax({
        url: getBaseUrl() + '_get_intercitation/' + src + "/" + dst,
        dataType: 'json',
        async: true,
        success: function (data) {
            console.log("received intercitation data");
            console.log(data);

            cb(data);
        },
        error: function (xhr, string, error) {
            resetGraph()
        }
    });
}


var grapher = {
    cy: null,
    reset: function () {
        clearGraph(this.cy);

        $("#samplesOpt").val(DEFAULT_SAMPLES);
        $("#algorithmOpt").val(DEFAULT_ALGO);

        getFullGraph(function (data) {
            this.cy = createCytoscapeGraph(data);
        });
    },
    drawIntercitation: function (src, dst) {
        clearGraph(this.cy);

        getIntercitationGraph(src, dst, function (data) {
            this.cy = createCytoscapeGraph(data);
        });
    },
    update: function (data) {
        clearGraph(this.cy);

        var algo = $("#algorithmOpt").val();
        var samples = $("#samplesOpt").val();

        getGraph(samples, algo, function(data) {
            this.cy = createCytoscapeGraph(data);
        });

    }
};

function refreshElements() {

    $.ajax({
        url: getBaseUrl() + '_get_cy_data',
        dataType: 'json',
        async: false,
        success: function (data) {
            //console.log(data)
            cydata = data;
            cydata.nodes.forEach(function (n) {
                n.grabbable = true;
                n.locked = false;
            });
        }
    });
}


function getIntercitationTree(src, dst) {
    $.ajax({
        url: getBaseUrl() + '_get_intercitation/' + src + "/" + dst,
        dataType: 'json',
        async: false,
        success: function (data) {
            intercitation = data;
            console.log(data);

            cy.destroy();
            cy = createNewVis(data);
            bindEvents();
        },
        error: function (xhr, string, error) {
            resetGraph()
        }
    });
}

function resetGraph() {

    clicked_nodes = [];
    if (cy != null) {
        cy.destroy();
    }

    refreshElements();
    console.log(cydata);
    cy = createNewVis(cydata);
    bindEvents();
}

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

            getIntercitationTree(clicked_nodes[0], clicked_nodes[1]);
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
    //resetGraph();
});
