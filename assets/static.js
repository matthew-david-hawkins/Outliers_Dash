
setTimeout(function(){

    alert('If you see this alert, then your custom JavaScript script has run!');
    var mydownload = d3.select("#download-button");
    console.log(mydownload);
    console.log(mydownload.attr('href'));
    console.log(mydownload.attr('download'));

    mydownload.on("click", function() {

        var inliers_csv = d3.select("#uploaded-inliers-csv").text();

        download(inliers_csv, "inliers.csv", "text/csv");

        var outliers_csv = d3.select("#uploaded-outliers-csv").text();

        download(outliers_csv, "outliers.csv", "text/csv");
    })

}, 3000);
