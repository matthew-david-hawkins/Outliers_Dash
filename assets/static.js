
setTimeout(function(){

    var mydownload = d3.select("#download-button");

    mydownload.on("click", function() {

        var inliers_csv = d3.select("#uploaded-inliers-csv").text();

        download(inliers_csv, "inliers.csv", "text/csv");

        var outliers_csv = d3.select("#uploaded-outliers-csv").text();

        download(outliers_csv, "outliers.csv", "text/csv");

    })

}, 3000);
