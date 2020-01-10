angular.module('auction').config([
  '$qProvider', '$logProvider', '$httpProvider', 'AuctionConfig', 'growlProvider', '$provide',
  function ($qProvider, $logProvider, $httpProvider, AuctionConfig, growlProvider, $provide) {
  $httpProvider.defaults.withCredentials = true;
//  $qProvider.errorOnUnhandledRejections(false);  TODO: wtf was this disabled
  $logProvider.debugEnabled(AuctionConfig.debug); // default is true
  growlProvider.globalTimeToLive({
    success: 4000,
    error: 10000,
    warning: 10000,
    info: 4000
  });
  growlProvider.globalPosition('top-center');
  growlProvider.onlyUniqueMessages(false);

  $provide.decorator('$log', [
    '$delegate', '$injector',
    function $logDecorator($delegate, $injector) {
      $delegate.context = {};

      var originalDebug = $delegate.debug;
      $delegate.debug = function decoratedDebug(msg) {
        if(AuctionConfig.debug){
          var sendLog = $injector.get('sendLog');
          sendLog(msg, "DEBUG", $delegate.context);
        }
        originalDebug.apply($delegate, arguments);
      };

      var originalInfo = $delegate.info;
      $delegate.info = function decoratedInfo(msg) {
        var sendLog = $injector.get('sendLog');
        sendLog(msg, "INFO", $delegate.context);
        originalInfo.apply($delegate, arguments);
      };
      $delegate.info.logs = originalInfo.logs;  // angular-mocks attribute

      var originalLog = $delegate.log;
      $delegate.log = function decoratedLog(msg) {
        var sendLog = $injector.get('sendLog');
        sendLog(msg, "INFO", $delegate.context);
        originalLog.apply($delegate, arguments);
      };

      var originalWarn = $delegate.warn;
      $delegate.warn = function decoratedWarn(msg) {
        var sendLog = $injector.get('sendLog');
        sendLog(msg, "WARNING", $delegate.context);
        originalWarn.apply($delegate, arguments);
      };

      var originalError = $delegate.error;
      $delegate.error = function decoratedError(msg) {
        var sendLog = $injector.get('sendLog');
        sendLog(msg, "ERROR", $delegate.context);
        originalError.apply($delegate, arguments);
      };

      return $delegate;
    }
  ]);

}]);