angular.module('auction').filter('floor', [function () {
  return function(value, precision) {
    precision = precision || 0;

    var format_function = function(val) {
      formatted = math.format(Number(val), {
        notation: 'fixed',
        precision: precision
      });
      parts = formatted.split(".");
      parts[0] = parts[0].replace(/(\d)(?=(\d{3})+$)/g, '$1 ');
      return parts.join(",");
    };

    if (!angular.isUndefined(value) && value !== "") {
      if (!angular.isNumber(value)){
        value = math.eval(math.format(math.fraction(value)));
      }
      var precision_module = Math.pow(10, precision);
      value = Math.floor(value * precision_module) / precision_module;
      return format_function(value);
    }
    return "";
  };
}]);
