function (doc) {
    if (doc.geo) {
        if (doc.id_str) {
            emit(doc.id_str, 1);
        } else if (doc.id) {
            emit(doc.id.toString(), 1);
        }
    }
}