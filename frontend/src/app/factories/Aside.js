angular.module('auction').factory('$aside', ['$uibModal', '$document', function ($uibModal, $document) {
  var asideFactory = {
    open: function(config) {
      var options = angular.extend({}, config);
      // check placement is set correct
      // set aside classes
      options.windowClass = 'ng-aside horizontal left' + (options.windowClass ? ' ' + options.windowClass : '');
      // delete options.placement
      return $uibModal.open(options);
    }
  };
  return angular.extend({}, $uibModal, asideFactory);
}]);