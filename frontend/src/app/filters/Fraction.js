angular.module('auction').filter('fraction', [function () {
  return function(val, coeficient) {
    var format_function = function(val) {
      return math.format(Number(val), {
        notation: 'fixed',
        precision: 2
      }).replace(/(\d)(?=(\d{3})+\.)/g, '$1 ').replace(/\./g, ",");
    };
    if (!angular.isUndefined(val)) {
      if (angular.isNumber(val)){
        return format_function(val);
      }
      if (coeficient) {
        return format_function(math.eval(math.format(math.fraction(val) * math.fraction(coeficient))).toFixed(2));
      }
      return format_function(math.eval(math.format(math.fraction(val))).toFixed(2));
    }
    return "";
  };
}]);


angular.module('auction').filter('fraction_string', [function () {
  return function(val) {
    return math.fraction(val).toString();
  };
}]);