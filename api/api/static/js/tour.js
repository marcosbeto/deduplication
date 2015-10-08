var tour = {
    plaza: { // First location: Plaza
        sides: [ // URLs for panorama files
            'img/cubified/myroom/posx.png',
            'img/cubified/myroom/negz.png',
            'img/cubified/myroom/negx.png',
            'img/cubified/myroom/posz.png',
            'img/cubified/myroom/posy.png',
            'img/cubified/myroom/negy.png'
        ],
          // '/path/to/plaza/right.jpg',
            // '/path/to/plaza/back.jpg',
            // '/path/to/plaza/left.jpg',
            // '/path/to/plaza/front.jpg',
            // '/path/to/plaza/up.jpg',
            // '/path/to/plaza/down.jpg'
        hotspots: [ // This location has 3 hotspot: navigation, info with video, and a link
            // { // Navigation hotspot which will take you to the Museum.
            //     type: 'nav',
            //     face: 0,
            //     x: 123,
            //     y: 456,
            //     id: 'nav-plaza-to-museum',
            //     name: 'Enter Museum',
            //     value: 'museum'
            // },
            // { // Link to the Leanorama repository
            //     type: 'link',
            //     face: 2,
            //     x: 42,
            //     y: 460,
            //     id: 'download-link',
            //     name: 'Download Leanorama',
            //     value:'https://github.com/leandigo/leanorama'
            // },
            // { // An info popup with a video
            //     type: 'info',
            //     face: 4,
            //     x: 1000,
            //     y: 1000,
            //     face: 0,
            //     id: 'info-video',
            //     name: 'That <em>awesome</em> video!',
            //     value: '<div id="blah" style="text-align: center">\
            //         <iframe width="200" height="113" src="http://www.youtube.com/embed/9bZkp7q19f0" frameborder="0" allowfullscreen></iframe>\
            //         <br><br>In case you have forgotten about this awesome video, here it is!<br><br>\
            //         <a href="http://youtu.be/9bZkp7q19f0" class="btn btn-success" target="_blank">Watch it on YouTube</a>\
            //         </div>'
            // }
        ]
    },
    // museum: { // Second location: Museum
    //     autorotate: 0.1         // When entering the location, autorotation will start
    //     sides: [ // URLs for panorama files
    //         '/path/to/museum/right.jpg',
    //         '/path/to/museum/back.jpg',
    //         '/path/to/museum/left.jpg',
    //         '/path/to/museum/front.jpg',
    //         '/path/to/museum/up.jpg',
    //         '/path/to/museum/down.jpg'
    //     ],
    //     hotspots: [
    //         { // A navigation hotspot to go back to the plaza
    //             type: 'nav',
    //             face: 2,
    //             x: 456,
    //             y: 789,
    //             id: 'nav-museum-to-plaza',
    //             name: 'Back to Plaza',
    //             value: 'plaza'
    //         },
    //     ]
    // }
};

// Initialize tour at the Plaza
var pano = $('#pano').leanorama(tour.plaza)

// Change location when navigational hotspots are clicked
// pano.on('leanoramaHotspotClick', function(e, hotspot) {
//     if (hotspot.type == 'nav') $(this).trigger('leanoramaRefresh', {tour[hotspot.value]});
// });