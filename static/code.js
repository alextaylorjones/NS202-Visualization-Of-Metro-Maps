var cy;
var cydata;
var intercitation;

var clicked_nodes = [];

function getBaseUrl() {
    var re = new RegExp(/^.*\//);
    return re.exec(window.location.href);
}

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

            cy = createNewVis(data);
        },
        error: function(xhr, string, error) {
            resetGraph()
        }
    });
}

function resetGraph() {
    clicked_nodes = [];
    refreshElements();
    console.log(cydata);
    if (cy != null) {
        cy.off();
    }
    cy = createNewVis(cydata);
    bindEvents();
}

function bindEvents() {
    //partial pull from http://stackoverflow.com/questions/20993149/how-to-add-tooltip-on-mouseover-event-on-nodes-in-graph-with-cytoscape-js
    cy.on('mouseover', 'node', function (event) {
        var n = event.cyTarget;

        var g = "<b>" + n.data('title') + "</b>" + '<br>Authors: ' + n.data('authors') + '<br>Abstract:<br>' + n.data('abstract');

        document.getElementById("tooltip").innerHTML = g

    });

    cy.on('click', 'node', function (event) {
        var n = event.cyTarget;
        console.log('clicked node length: ' + clicked_nodes.length);

        if (clicked_nodes.length == 1 && $.inArray(n.data('id'),  clicked_nodes) != -1){
            cy.$('#'+ n.data('id')).style('background-color', '#11479e');
            clicked_nodes = [];
            console.log("cleared background: " + n.data('id'))
        } else if (clicked_nodes.length == 1 && $.inArray(n.data('id'), clicked_nodes) == -1) {

            clicked_nodes.push(n.data('id'));
            console.log("intercitation for these nodes: " + clicked_nodes)

            getIntercitationTree(clicked_nodes[0], clicked_nodes[1]);
            clicked_nodes =[];
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

    resetGraph();
    //bindEvents();


    //var intervalID = setInterval(function () {
    //    cy.nodes().forEach(function (n) {
    //        n.renderedPosition(
    //            {
    //                x: Math.floor(Math.random() * 1000),
    //                y: Math.floor(Math.random() * 1000)
    //            }
    //        );
    //    });
    //}, 5000);
//
//    var params = {
//        name: 'Dagre',
//        nodeSpacing: 5,
//        edgeLengthVal: 45,
//        animate: true,
//        randomize: false,
//        maxSimulationTime: 1500
//    };
//    var layout = makeLayout();
//    var running = false;
//
//    cy.on('layoutstart', function () {
//        running = true;
//    }).on('layoutstop', function () {
//        running = false;
//    });
//
//
//    layout.run();
//
//    var $config = $('#config');
//    var $btnParam = $('<div class="param"></div>');
//    $config.append($btnParam);
//
//    var sliders = [
//        {
//            label: 'Edge length',
//            param: 'edgeLengthVal',
//            min: 1,
//            max: 200
//        },
//
//        {
//            label: 'Node spacing',
//            param: 'nodeSpacing',
//            min: 1,
//            max: 50
//        }
//    ];
//
//    var buttons = [
//        {
//            label: '<i class="fa fa-random"></i>',
//            layoutOpts: {
//                randomize: true,
//                flow: null
//            }
//        },
//
//        {
//            label: '<i class="fa fa-long-arrow-down"></i>',
//            layoutOpts: {
//                flow: {axis: 'y', minSeparation: 30}
//            }
//        }
//    ];
//
//    sliders.forEach(makeSlider);
//
//    buttons.forEach(makeButton);
//
//    function makeLayout(opts) {
//        params.randomize = false;
//        params.edgeLength = function (e) {
//            return params.edgeLengthVal / e.data('weight');
//        };
//
//        for (var i in opts) {
//            params[i] = opts[i];
//        }
//
//        return cy.makeLayout(params);
//    }
//
//    function makeSlider(opts) {
//        var $input = $('<input></input>');
//        var $param = $('<div class="param"></div>');
//
//        $param.append('<span class="label label-default">' + opts.label + '</span>');
//        $param.append($input);
//
//        $config.append($param);
//
//        var p = $input.slider({
//            min: opts.min,
//            max: opts.max,
//            value: params[opts.param]
//        }).on('slide', _.throttle(function () {
//            params[opts.param] = p.getValue();
//
//            layout.stop();
//            layout = makeLayout();
//            layout.run();
//        }, 16)).data('slider');
//    }
//
//    function makeButton(opts) {
//        var $button = $('<button class="btn btn-default">' + opts.label + '</button>');
//
//        $btnParam.append($button);
//
//        $button.on('click', function () {
//            layout.stop();
//
//            if (opts.fn) {
//                opts.fn();
//            }
//
//            layout = makeLayout(opts.layoutOpts);
//            layout.run();
//        });
//    }
//
//    function restyleIntercitationTree() {
//
//        cy.startBatch();
//
//        var ele = intercitation.elements();
//
//        for (var i = 0; i < ele.length; i++) {
//            var ele = ele[i];
//
//            console.log(ele.id() + ' is ' + ( ele.selected() ? 'selected' : 'not selected' ));
//
//        }
//
//        cy.endBatch();
//    }
//

});