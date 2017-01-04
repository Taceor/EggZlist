function changeImage(path) 
{
  document.getElementById("big-picture").src = path
}

function save_item(user_id, item_id)
{
  $.get(
      url="/_save_item",
      data={
        item_id:item_id,
        user_id:user_id
      },
      success=function() {
        alert("Saved");
      });
}

function initialize()
{
  var mapProp = {
    center: new google.maps.LatLng(38.8922, -104.7995),
    zoom:10,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var map = new google.maps.Map(document.getElementById("googleMap"),mapProp);
  var geocoder = new google.maps.Geocoder();
  var zipcode = document.getElementById("zipcode").innerHTML;
  var address = document.getElementById("citystate").innerHTML;
  var street = document.getElementById("street").innerHTML;
  var listing_id = document.getElementById("listing_id").innerHTML;
  if (address && street) {
     geocoder.geocode( { 'address': street+address}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
          var marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location,
          title: 'Location'
          });
          map.setCenter(results[0].geometry.location);
          $.get(
            url="/_set_user_latlng",
            data={
                lat:results[0].geometry.location.lat(),
                lng:results[0].geometry.location.lng(),
                listing_id:listing_id
            },
            success=function(data) {
            });
        } else {
          alert("Could not find location: " + street + " " + address);
        }
      });

  } else {
      geocoder.geocode( { 'address': zipcode}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
          var marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location,
          title: 'Location'
          });
          map.setCenter(results[0].geometry.location);
          $.get(
            url="/_set_user_latlng",
            data={
                lat:results[0].geometry.location.lat(),
                lng:results[0].geometry.location.lng(),
                listing_id:listing_id
            },
            success=function(data) {
            });
        } else {
          alert("Could not find location: " + zipcode);
        }
      });
  }
}

google.maps.event.addDomListener(window, 'load', initialize);


// Filter button pop up
// $(function() {
//   $("#filter").on("click", function(){
//     if ($(".filter-block-outer").hasClass("visible")) {
//       $(".filter-block-outer").removeClass("visible");
//     } else{
//       $(".filter-block-outer").addClass("visible");
//     };
//   });
// });

// Make sure window is loaded before executing
window.onload = function() {

  // Get the modal
  var modal = document.getElementById("filter-modal-js");

  // Get the button that opens the modal
  var button = document.getElementById("filter-button");

  // Get the span element that closes the modal
  var close = document.getElementsByClassName("close")[0];

  // When user clicks the button, open the modal
  button.onclick = function() {
    modal.style.display = "block";
  };

  // When the user clicks on <span> x close the modal
  close.onclick = function() {
    modal.style.display = "none";
  };

  // When the user clicks anywhere outside the modal, close it
  // 'modal' is the background
  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    };
  };
};
