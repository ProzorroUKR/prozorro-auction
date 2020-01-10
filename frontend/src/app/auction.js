var appRequires = [
  'ui.bootstrap',
  'ngCookies',
  'pascalprecht.translate',
  'timer',
  'angular-growl',
  'angular-ellipses',
];

var db = {},
    bidder_id = "0",
    db_url = db_url || (location.protocol + '//' + location.host + '/' + window.db_name ) || "";


angular.module('auction', appRequires)
  .constant('AuctionConfig', {
    remote_db: db_url,
    restart_retries: 10,
    default_lang: 'uk',
    debug: false })
