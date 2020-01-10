angular.module('auction').filter('eval_string', [function () {
  return function(val) {
    return math.eval(val);
  };
}]);