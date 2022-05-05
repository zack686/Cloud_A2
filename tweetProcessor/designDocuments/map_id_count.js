function (doc) {
    if (doc.geo) {
        if (doc.id_str) {
            emit(doc.id_str);
        } else if (doc.id) {
            emit(doc.id.toString());
        }
    }
}