var cy;

var cydata;

var intercitation;

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
                n.grabbable = false;
                n.locked = false;
            });
        }
    });
}

function getIntercitationTree(node_id) {
    $.ajax({
        url: getBaseUrl() + '_get_intercitation_' + node_id,
        dataType: 'json',
        async: false,
        success: function (data) {
            console.log(data)
            intercitation = data;
            intercitation.nodes.forEach(function (n) {
                var x = cydata.$(n.data.name);
                x.grabbable = true;
            });
        }
    });


}

refreshElements()

$(function () { // on dom ready


    console.log('test')
    console.log(cydata)

    var cy = cytoscape({
        container: document.getElementById('cy'),


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
                    'width': 4,
                    'target-arrow-shape': 'triangle',
                    'line-color': '#9dbaea',
                    'target-arrow-color': '#9dbaea'
                }
            }
        ],

        elements: cydata
    });


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

    var params = {
        name: 'cola',
        nodeSpacing: 5,
        edgeLengthVal: 45,
        animate: true,
        randomize: false,
        maxSimulationTime: 1500
    };
    var layout = makeLayout();
    var running = false;

    cy.on('layoutstart', function () {
        running = true;
    }).on('layoutstop', function () {
        running = false;
    });


    layout.run();

    var $config = $('#config');
    var $btnParam = $('<div class="param"></div>');
    $config.append($btnParam);

    var sliders = [
        {
            label: 'Edge length',
            param: 'edgeLengthVal',
            min: 1,
            max: 200
        },

        {
            label: 'Node spacing',
            param: 'nodeSpacing',
            min: 1,
            max: 50
        }
    ];

    var buttons = [
        {
            label: '<i class="fa fa-random"></i>',
            layoutOpts: {
                randomize: true,
                flow: null
            }
        },

        {
            label: '<i class="fa fa-long-arrow-down"></i>',
            layoutOpts: {
                flow: {axis: 'y', minSeparation: 30}
            }
        }
    ];

    sliders.forEach(makeSlider);

    buttons.forEach(makeButton);

    function makeLayout(opts) {
        params.randomize = false;
        params.edgeLength = function (e) {
            return params.edgeLengthVal / e.data('weight');
        };

        for (var i in opts) {
            params[i] = opts[i];
        }

        return cy.makeLayout(params);
    }

    function makeSlider(opts) {
        var $input = $('<input></input>');
        var $param = $('<div class="param"></div>');

        $param.append('<span class="label label-default">' + opts.label + '</span>');
        $param.append($input);

        $config.append($param);

        var p = $input.slider({
            min: opts.min,
            max: opts.max,
            value: params[opts.param]
        }).on('slide', _.throttle(function () {
            params[opts.param] = p.getValue();

            layout.stop();
            layout = makeLayout();
            layout.run();
        }, 16)).data('slider');
    }

    function makeButton(opts) {
        var $button = $('<button class="btn btn-default">' + opts.label + '</button>');

        $btnParam.append($button);

        $button.on('click', function () {
            layout.stop();

            if (opts.fn) {
                opts.fn();
            }

            layout = makeLayout(opts.layoutOpts);
            layout.run();
        });
    }

    function restyleIntercitationTree() {

        cy.startBatch();

        var ele = intercitation.elements();

        for (var i = 0; i < ele.length; i++) {
            var ele = ele[i];

            console.log(ele.id() + ' is ' + ( ele.selected() ? 'selected' : 'not selected' ));

        }

        cy.endBatch();
    }

    //partial pull from http://stackoverflow.com/questions/20993149/how-to-add-tooltip-on-mouseover-event-on-nodes-in-graph-with-cytoscape-js
    cy.on('mouseover', 'node', function (event) {
        var n = event.cyTarget;
        //getIntercitationTree(parseInt(n.data('file_id')));

        n.qtip({
            content: n.data('title'),
            show: {
                event: event.type//,
                //ready: true
            },
            hide: {
                event: 'mouseout unfocus'
            }
        }, event);
    });

    cy.on('click', 'node', function (event) {
        //cy.nodes().forEach(function (n) {
        var n = event.cyTarget;
        var g = "<b>" + n.data('title') + "</b>" + '<br>Authors: ' + n.data('authors') + '<br>Abstract:<br>' + n.data('abstract');

        //Updates the intercitation var
        getIntercitationTree(parseInt(n.data('file_id')));
//        restyleIntercitationTree();

        n.qtip({
            content: g,
            position: {
                my: 'top center',
                at: 'bottom center'
            },
            style: {
                classes: 'qtip-bootstrap',
                tip: {
                    width: 45,
                    height: 8
                }
            }
        });
    });

    //$('#config-toggle').on('click', function () {
    //    $('body').toggleClass('config-closed');

    //  cy.resize();
    //});
    function getIntercitationTree(node_id) {
        $.ajax({
            url: getBaseUrl() + '_get_intercitation_' + node_id,
            dataType: 'json',
            async: false,
            success: function (data) {
                intercitation = data;

                console.log(intercitation);
                intercitation.nodes.forEach(function (node) {
                    var node_data = node['data'];

                    var paper_name = node_data['name'];
                    //var query = "[source='" + pape + "']";

                    console.log(paper_name);
                    console.log(cy.$('#' + paper_name));
                    cy.$('#' + paper_name).renderedPosition({
                        x: Math.floor(Math.random() * 200) - 200,
                        y: Math.floor(Math.random() * 200) - 200
                    });


                    //console.log(cy.getElementById(paper_name));
                    //console.log(query);
                    //
                    //var collection = cy.elements("node[name='" + paper_name + "']");
                    ////matched_paper = cy.edges(query);
                    //console.log(collection);
                    //
                    //collection.forEach(function (foundNode) {
                    //    console.log("node");
                    //    console.log(foundNode)
                    //});


                });
                //intercitation.nodes.forEach(function(n){
                //  var x = cydata.$(n.data.name);
                //   x.grabbable = true;
                //   });
            }
        });

    }

}); // on dom ready

$(function () {
    FastClick.attach(document.body);
});
