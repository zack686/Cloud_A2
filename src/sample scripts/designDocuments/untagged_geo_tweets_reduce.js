function (keys, values, rereduce) {
    if (rereduce) {
      var res = [];
      for (var i = 0; i < values.length; i++){
        res = res.concat(values[i])
      }
      return res;
    } else {
      return values;
    }
  }