

//d3.json('test.json', function(data){
//  console.log(data.id);
  //data.forEach(function(d,i) {
    //var div = new Div();
    //console.log('test');
  //})
//})

var chart = {
  height: 1100,
  width: 2200,
  imgsize:80,
}

d3.select("#main")
  .attr("width",chart.width)
  .attr("height",chart.height)



var canvas = document.querySelector('#main'),
    ctx = canvas.getContext('2d');

    ctx.beginPath();
    ctx.rect(0, 0, chart.width,chart.height);
    ctx.fillStyle = 'black';
    ctx.fill();

d3.tsv('localhost:7900/analysis01_features_umap.tsv').then(function(data){

  //console.log(d3.extent(data,function(d) { return d.x }))
  var x = d3.scaleLinear()
    .domain(d3.extent(data, function(d) { return d.umap_x }))
    .range([80, chart.width - 80])

  var y = d3.scaleLinear()
    .domain(d3.extent(data, function(d) { return d.umap_y }))
    .range([140, chart.height - 140])

    //.attr("src","images/"+data.images)


  //maindiv.selectAll("div")
  data.forEach(function(d,i) {

    var img = new Image();

    img.onload = function() {
        ctx.mozImageSmoothingEnabled = false;
        ctx.webkitImageSmoothingEnabled = false;
        ctx.msImageSmoothingEnabled = false;
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(img,x(d.x),y(d.y),chart.imgsize,chart.imgsize*img.height/img.width);
      }
    img.src = "images/"+d.image;

      //.attr("src","images/"+d.image)

  })
  console.log(canvas)
});
