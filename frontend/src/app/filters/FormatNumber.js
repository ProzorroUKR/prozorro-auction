angular.module('auction').filter('formatnumber', ['$filter', function ($filter) {
  return function(val) {
    return ($filter('number')(val) || "").replace(/,/g, " ") || "";
  };
}]);