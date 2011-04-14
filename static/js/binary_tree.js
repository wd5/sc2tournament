//don't lose the prototype when we get rid of the mouse events.
var p = Graph.Renderer.Raphael.prototype;

Graph.Renderer.Raphael = function(element, graph, width, height) {
    this.width = width || 400;
    this.height = height || 400;
    var selfRef = this;
    this.r = Raphael(element, this.width, this.height);
    this.radius = 40; /* max dimension of a node */
    this.graph = graph;
    this.mouse_in = false;

    /* TODO default node rendering function */
    if(!this.graph.render) {
        this.graph.render = function() {
            return;
        }
    }
    this.draw();
};
//put it back ;)
Graph.Renderer.Raphael.prototype = p;


//custom render function, to be used as the default for every node
var render = function(r, s) {
	var display_name = "";
	
	/* Figure out what to display text wise on node... */
	
	//see how many teams are in this set
	if(s.competing_teams.length >=1 ) {
		
		display_name += getTeamDisplay(s.competing_teams[0]) + "\nVS\n";
		if(s.competing_teams[1]) {
			/* if we have two teams, show the second team and their scores */
			display_name += getTeamDisplay(s.competing_teams[1]);
			display_name += "\n" + getMatchScores(s);
		}
	}

	
	
	/* All the drawing code down here */
    var set = r.set().push(r.rect(s.point[0], s.point[1], 150, 90).attr({"fill": "#fa8", "stroke-width": 2}));
    
    if(display_name != "")	//for some reason empty strings can't be rendered properly in RaphaelJS...
	    set.push(r.text(s.point[0] + 75, s.point[1] + 45, display_name).attr({'font-size' : 15}));
    return set;
};


/* Takes a Team json map as t and returns a display value */
function getTeamDisplay(t) {
	//check to see what the tournamentJson sez is our size
	if(tournamentJson.size_of_teams == 1) {
		//by themselves just show player information
		return t.leader.name + "#" + t.leader.character_code;
	}
	return t.name;
}

/* Takes a Set and calculates the score aka 3-2 status 
 * function should only be called when we have two teams in set...
 */
function getMatchScores(s) {
	console.info(s);
	sums = {};
	for(var m in s.matches) {
		//bah, make sure its a number before you can do +=...
		if(!sums[getTeamDisplay(s.matches[m].winner)])
			sums[getTeamDisplay(s.matches[m].winner)] = 0;

		sums[getTeamDisplay(s.matches[m].winner)] = 1;
	}
	//make sure the order is what we expect..
	var r = "";
	if(sums[getTeamDisplay(s.competing_teams[0])])
		r += sums[getTeamDisplay(s.competing_teams[0])] + " - ";
	else
		r += "0 - ";
		
	if(sums[getTeamDisplay(s.competing_teams[1])])
		r += sums[getTeamDisplay(s.competing_teams[1])];
	else
		r += "0";
	return r;
}

var layouter;
var renderer;
var tournamentJson;
function renderTournament(id) {
	//make our render function the default
	Graph.Renderer.defaultRenderFunc = render;
	
    var width = 1000;
    var height = 800;

	//get the tournament info
	$.getJSON('/tournament/tournament/info/'+id+'/', function(data) {
		tournamentJson = data;	//keep it around for referencing later.
		//create the graph when we got data to draw.
	    g = new Graph();
	    
		//create all the nodes with our json data for the set.
		$.each(data['sets'], function(key,value) {
			g.addNode(value.set_number, value);
		});
		
		//create all edges for this tournament
		console.info(data['sets'].length);
		for(var i = data['sets'].length; i > 1; i--) {
			console.info("Adding edge (" + i + ", " + Math.floor(i/2) + ")");
			g.addEdge(i, Math.floor(i/2));
		}
		
		//draw the svg
		layouter = new Graph.Layout.TournamentTree(g, nodeid_sort(g));
	    renderer = new Graph.Renderer.Raphael('canvas', g, width, height);
	});
}


/* blah can't get this working yet... */
/*
    var r = new Raphael('test_badge', width, height);
    var rect = r.rect(0,0,200,300).attr({"fill" : "#fa8"});
    var img = r.rect(0,0,75,75).attr({"fill" : "url(/static/img/portraits-0-75.jpg)"});
*/
    
