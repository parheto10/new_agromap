const icon = L.icon({
  iconSize: [25, 41],
  iconAnchor: [10, 41],
  popupAnchor: [2, -40],
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png"
});

// Promise.all([
//   fetch("http://127.0.0.1:8000/parif/api/planting_parif/v1/"),
//   fetch("http://127.0.0.1:8000/parif/api/details_planting_parif/v1/")
// ]).then(async ([response1, response2]) => {
//   const responseData1 = await response1.json();
//   const responseData2 = await response2.json();

Promise.all([
  fetch("http://127.0.0.1:8000/parif/api/planting_parif/v1/"),
  fetch("http://127.0.0.1:8000/parif/api/details_planting_parif/v1/")
]).then(async ([response1, response2]) => {
  const responseData1 = await response1.json();
  const responseData2 = await response2.json();

  const data1 = responseData1;
  const data2 = responseData2;
  console.log(data2);
  const plantings = L.featureGroup().addTo(map);

data1.forEach(({ parcelle, plant_total, campagne, projet, date,  id: id }) => {
    plantings.addLayer(
      L.marker([parcelle.latitude, parcelle.longitude], { icon }).bindPopup(
        `
          <table class="table table-striped table-bordered" style="width: 550px">
            <h4 class="text-center" style="font-weight: bold">
                    PARCELLE : ${parcelle.code_parcelle} <br>
                    PROPRIETAIRE : ${parcelle.proprietaire} <br>
                    PLANTS RECUS : ${plant_total}
            </h4>
            <thead style="align-items: center">
                <tr>
<!--                  <th scope="col" class="center">PARCELLE</th>-->
                  <th scope="col" class="text-center">ESPECE</th>
                  <th scope="col" class="text-center">QUANTITE</th>
                  <th scope="col" class="text-center">DATE</th>
                </tr>
            </thead>
            <tbody style="align-items: center">
                <tr>
<!--                    <td class="text-uppercase"><strong>${parcelle.code_parcelle}</strong></td>-->
                    <td class="text-uppercase text-center"><strong>${data2.find((d) => (d.id) === (id)).espece_libelle}</strong></td>
                    <td class="text-uppercase text-center"><strong>${data2.find((d) => Number(d.id) === Number(id)).nb_plante}</strong></td>
                    <td class="text-uppercase text-center"><strong>${date}</strong></td>
                </tr>
            </tbody>
          </table>
        `
      )
    );
  });
<!--                        (${espece.libelle}==>${nb_plante})-->
//  map.fitBounds(plantings.getBounds());
});

//Initialisation de la Map
var map = L.map('map').setView([7.539989, -5.547080], 7);
map.zoomControl.setPosition('topright');

var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
 maxZoom: 22,
 attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors - @Copyright - Agro-Map CI'
}).addTo(map);

//map Climat
var climat = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
 maxZoom: 22,
 attribution: '@Copyright - Agro-Map CI - Plantings'
});


// Ajouter Popup de Marquage
var singleMarker = L.marker([5.349390, -4.017050])
 .bindPopup("Bienvenus en .<br> Côte d'Ivoire.")
 .openPopup();

// Ajouter Calcul de Distance
L.control.scale().addTo(map);

//Afficher les Coordonnées sur la carte
map.on('mousemove', function (e) {
 //console.log(e);
 $('.coordinates').html(`lat: ${e.latlng.lat}, lng: ${e.latlng.lng}`)
});


//Charger les Villes sur la Carte
//L.geoJSON(data).addTo(map);
var marker = L.markerClusterGroup();
marker.addTo(map);

// Laeflet Layer control
var baseMaps = {
 'ROUTE': osm,
 'COUVERT FORESTIER': climat,
}

var markers = L.markerClusterGroup({
	spiderfyShapePositions: function(count, centerPt) {
        var distanceFromCenter = 35,
            markerDistance = 45,
            lineLength = markerDistance * (count - 1),
            lineStart = centerPt.y - lineLength / 2,
            res = [],
            i;

        res.length = count;

        for (i = count - 1; i >= 0; i--) {
            res[i] = new Point(centerPt.x + distanceFromCenter, lineStart + markerDistance * i);
        }

        return res;
    }
});

var overLayMaps = {
 // 'VILLES' : marker,
 // 'ABIDJAN': singleMarker
}
L.control.layers(baseMaps, overLayMaps, {collapse :false, position: 'topleft'}).addTo(map);




