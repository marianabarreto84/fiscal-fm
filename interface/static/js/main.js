$(document).ready(function() {
    $('#scrobblesTable').DataTable({
        "ajax": {
            "url": "/data",
            "dataSrc": ""
        },
        "columns": [
            { "data": "username" },
            { "data": "artist" },
            { "data": "track" },
            { "data": "scrobble_date"}
            // Adicione mais colunas conforme necessário
        ]
    });
});
