//SET UP EXPRESS
var express = require('express');
var app = express();

//For config files
var fs = require('fs');
var path = require('path');

//For executing python script
var spawnSync = require("child_process").spawnSync;

var bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({extended:false}));
app.use(bodyParser.json());

var engines = require('consolidate');
app.engine('html', engines.hogan); // tell Express to run .html files through Hogan
app.set('views', __dirname); // tell Express where to find templates, in this case the '/templates' directory
app.set('view engine', 'html'); //register .html extension as template engine so we can render .html pages 

app.use(express.static(__dirname + '/public')); //client-side js & css files

var stateCodes = {
			    "AL": "Alabama","AK": "Alaska","AZ": "Arizona","AR": "Arkansas","CA": "California","CO": "Colorado","CT": "Connecticut","DE": "Delaware","DC": "District Of Columbia","FL": "Florida","GA": "Georgia","HI": "Hawaii","ID": "Idaho","IL": "Illinois","IN": "Indiana","IA": "Iowa","KS": "Kansas","KY": "Kentucky","LA": "Louisiana","ME": "Maine","MD": "Maryland","MA": "Massachusetts","MI": "Michigan","MN": "Minnesota","MS": "Mississippi","MO": "Missouri","MT": "Montana","NE": "Nebraska","NV": "Nevada","NH": "New Hampshire","NJ": "New Jersey","NM": "New Mexico","NY": "New York","NC": "North Carolina","ND": "North Dakota","MP": "Northern Mariana Islands","OH": "Ohio","OK": "Oklahoma","OR": "Oregon","PA": "Pennsylvania","PR": "Puerto Rico","RI": "Rhode Island","SC": "South Carolina","SD": "South Dakota","TN": "Tennessee","TX": "Texas","UT": "Utah","VT": "Vermont","VA": "Virginia","WA": "Washington","WV": "West Virginia","WI": "Wisconsin","WY": "Wyoming"
			}

//ROUTING
app.get('/', function(req, res){
	console.log('- Request received:', req.method);
	res.render('index.html');
});

app.get('/state/:name', function(req, res){

	var rawdata = fs.readFileSync('states.json');
	var state = JSON.parse(rawdata).features.find(state => (state.properties.NAME == stateCodes[req.params.name]));

	var	stateGeom = state.geometry;//get the geometry/coordinates corresponding to the state in question
	var zoom = (11.5 - Math.log10(state.properties.CENSUSAREA));
	console.log(zoom);


	fs.readFile('../district_polygons/polygons_'+req.params.name, 'utf8', function(err, data){

		if (err){
			console.log('yay');
			console.log(err);
			res.redirect('/redistrict/'+req.params.name+'/6');
		}
		else {
			var polygons = JSON.parse(data.replace(/\(/g, '\[').replace(/\)/g, '\]'));
			var adjusted = [];

			//data is off for some reason so i fix it here... will eventually not be necessary
			var scale = 1-parseInt(stateGeom.center[0]);
			for (var i in polygons){
				var truPoly = polygons[i].map(coord => [coord[0]-scale, coord[1]]);
				console.log(truPoly);
				adjusted.push(truPoly);
			}
			var json = {"polygons":adjusted, "geometry":stateGeom, "zoom":zoom};

			res.send(JSON.stringify(json));

		}

	});


});

app.get('/states', function(req, res){
	res.send(JSON.stringify(stateCodes));
})

app.get('/redistrict/:name/:districts', function(req, res){


	var childprocess = spawnSync('python3',["../do_redistrict.py", req.params.districts, req.params.name]);

	//childprocess.on('exit', (err) => {
	//	console.log(err);
  	//	console.log('Failed to start subprocess.');
	//});

	console.log(childprocess.stderr.toString('utf8'));
	//console.log(childprocess.stdout);

	res.redirect('/state/'+req.params.name);
});

app.post('/redistrict', function(req, res){
	var k = req.body.number;
	var state = req.body.state;

	var childprocess = spawnSync('python3',["../do_redistrict.py", k, state]);

})
//SERVER SET UP

app.listen(8080, function(){
	console.log('– Server listening on port 8080');
});

process.on('SIGINT', function(){
	console.log('\nI\'m closing');
	process.exit(0);
});