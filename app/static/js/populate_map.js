function populate()
{
  var mapProp = {
    center: new google.maps.LatLng(38.8922, -104.7995),
    zoom:10,
  };
  var map = new google.maps.Map(document.getElementById("googleMap"),mapProp);
  var im = 'http://www.robotwoods.com/dev/misc/bluecircle.png';
  google.maps.event.addListener(map,'idle',function() {
    //send bounds to flask
    var bounds = map.getBounds();
    var ne = bounds.getNorthEast();
    var sw = bounds.getSouthWest();
    $.get(
      url="_markmap",
      data={
        swlat:sw.lat(),
        swlng:sw.lng(),
        nelat:ne.lat(),
        nelng:ne.lng()
      },
      // returned markers
      success=function(data) {
        for (var i in data.local_users) {
          var marker = new google.maps.Marker({
            position: {lat: data.local_users[i].lat, lng: data.local_users[i].lng},
            title: data.local_users[i].name,
            map: map
          });
        }
      }
    );
  });
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };
      marker = new  google.maps.Marker({
        position: pos,
        title: 'Your Location',
        map: map,
        icon: im
      });
      map.setCenter(pos);
    }, function() {
      handleLocationError(true, infoWindow, map.getCenter());
    });
  } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
  }
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(browserHasGeolocation ?
                        'Error: Geolocation failed.' :
                        'Error: Your browser does not support geolocation.');
}

google.maps.event.addDomListener(window, 'load', populate);
