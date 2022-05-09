function (doc) {
    if (doc.geo && doc.id_str) {
        emit(doc.id_str, 1);
    }
}