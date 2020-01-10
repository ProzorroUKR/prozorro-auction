angular.module('auction').controller('ListingController',[
  'AuctionConfig', '$scope', '$http',
  function (AuctionConfig, $scope, $http) {
  /*@ngInject;*/
  $scope.url = location.protocol + '//' + location.host + '/tenders';
  $http({
    method: 'GET',
    url: '/api/auctions',
    cache: true,
  }).then(function(resp) {
    $scope.auctions = resp.data;
  });
}]);