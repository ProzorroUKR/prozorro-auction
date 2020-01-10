angular.module('auction').controller('OffCanvasController', [
    '$rootScope', '$modalInstance',
    function ($scope, $modalInstance) {
  $rootScope.allert = function() {
    console.log($rootScope);
  };
  $rootScope.ok = function() {
    $modalInstance.close($rootScope.selected.item);
  };
  $rootScope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };
}]);
