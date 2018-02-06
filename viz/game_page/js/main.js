$(document).ready(function() {
      plot_rotations();

      var courtSelection = d3.select("#shot-chart");
      var court = d3.court().width(600);
      courtSelection.call(court);

      $.getJSON("./data/shots.json", function(json) {
          data = json;
  				players = [];
  				$.each(data, function(i, d){
  					if ($.inArray(this.shooter, players) === -1){
  						players.push(this.shooter);
  					}
  				});
  				$.each(players, function(i, p){
  					$('#player-select').append($('<option></option>').val(p).html(p));
  				});

          $('#player-select').val($('#player-select option:first').val()).change();
      });

      $('#player-select').change(function(){
        player = $('#player-select option:selected').val();
        player_data = data.filter(function(d) {
          return d.player == player;
        });
        console.log(player_data);
        var shots = d3.shots().shotRenderThreshold(1).displayToolTips(true).displayType("scatter");
        courtSelection.datum(player_data).call(shots);
      });

      create_stats_table();
});
