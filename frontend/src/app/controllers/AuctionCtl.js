angular.module('auction').controller('AuctionController',[
  'AuctionConfig', 'AuctionUtils',
  '$timeout', '$http', '$log', '$cookies', '$cookieStore', '$window',
  '$rootScope', '$location', '$translate', '$filter', 'growl', 'growlMessages', '$aside', '$q',
  function(AuctionConfig, AuctionUtils,
  $timeout, $http, $log, $cookies, $cookieStore, $window,
  $rootScope, $location, $translate, $filter, growl, growlMessages, $aside, $q)
  {
    var base_url = window.location.href.replace(window.location.search, '');
    var evtSrc = '';
    var response_timeout = '';

    if (AuctionUtils.inIframe() && 'localhost'!= location.hostname) {
      $log.error('Starts in iframe');
      window.open(location.href, '_blank');
      return false;
    }

    AuctionConfig.auction_doc_id = window.location.pathname.replace('/tenders/', '');

    $rootScope.lang = 'uk';
    $rootScope.normilized = false;
    $rootScope.format_date = AuctionUtils.format_date;
    $rootScope.bidder_id = null;
    $rootScope.bid = null;
    $rootScope.follow_login_allowed = false;
    $rootScope.allow_bidding = true;
    $rootScope.form = {};
    $rootScope.alerts = [];
    $rootScope.default_http_error_timeout = 500;
    $rootScope.http_error_timeout = $rootScope.default_http_error_timeout;
    $rootScope.browser_client_id = AuctionUtils.generateUUID();
    window.onunload = function () {
      $log.info("Close window")
      if($rootScope.changes){
        $rootScope.changes.cancel()
      }
      if($rootScope.evtSrc){
        $rootScope.evtSrc.close();
      }
    }

    if (AuctionConfig.auction_doc_id.indexOf("_") > 0 ){
      var doc_id_parts =  AuctionConfig.auction_doc_id.split("_")
      $log.context["TENDER_ID"] = doc_id_parts[0];
      $log.context["LOT_ID"] = doc_id_parts[1];
    } else {
      $log.context["TENDER_ID"] = AuctionConfig.auction_doc_id;
    }
    $log.info({
      message: "Start session",
      browser_client_id: $rootScope.browser_client_id,
      user_agent: navigator.userAgent
    })
    $rootScope.change_view = function() {
      if ($rootScope.bidder_coeficient) {
        $rootScope.normilized = !$rootScope.normilized;
      }
    };
    $rootScope.growlMessages = growlMessages;
    growlMessages.initDirective(0, 10);
    if (($translate.storage().get($translate.storageKey()) === "undefined") || ($translate.storage().get($translate.storageKey()) === undefined)) {
      $translate.use(AuctionConfig.default_lang);
      $rootScope.lang = AuctionConfig.default_lang;
    } else {
      $rootScope.lang = $translate.storage().get($translate.storageKey()) || $rootScope.lang;
    }

    /*      Time stopped events    */
    $rootScope.$on('timer-stopped', function(event) {
      if (($rootScope.auction_doc) && (event.targetScope.timerid == 1) && ($rootScope.auction_doc.current_stage == -1)) {
        if (!$rootScope.auction_not_started){
          $rootScope.auction_not_started = $timeout(function() {
            if($rootScope.auction_doc.current_stage === -1){
              growl.warning('Please wait for the auction start.', {ttl: 120000, disableCountDown: true});
              $log.info({message: "Please wait for the auction start."});
            }
          }, 10000);
        }

        $timeout(function() {
          if($rootScope.auction_doc.current_stage === -1){
            $rootScope.sync_times_with_server();
          }
        }, 120000);
      }
    });
    /*      Time tick events    */
    $rootScope.$on('timer-tick', function(event) {
      if (($rootScope.auction_doc) && (event.targetScope.timerid == 1)) {
        if (((($rootScope.info_timer || {}).msg || "") === 'until your turn') && (event.targetScope.minutes == 1) && (event.targetScope.seconds == 50)) {
          $http.post(base_url + '/check_authorization').then(function(data) {
            $log.info({
              message: "Authorization checked"
            });
          }, function(data) {
            $log.error({
              message: "Error while check_authorization"
            });
            if (data.status == 401) {
              growl.error('Ability to submit bids has been lost. Wait until page reloads.');
              $log.error({
                message: "Ability to submit bids has been lost. Wait until page reloads."
              });
              $timeout(function() {
                window.location.replace(window.location.href + '/relogin');
              }, 3000);
            }
          });
        };
        $timeout(function() {
          $rootScope.time_in_title = event.targetScope.days ? (event.targetScope.days + $filter('translate')('days') + " ") : "";
          $rootScope.time_in_title += event.targetScope.hours ? (AuctionUtils.pad(event.targetScope.hours) + ":") : "";
          $rootScope.time_in_title += (AuctionUtils.pad(event.targetScope.minutes) + ":");
          $rootScope.time_in_title += (AuctionUtils.pad(event.targetScope.seconds) + " ");
        }, 10);
      } else {
        var date = new Date();
        $rootScope.seconds_line = AuctionUtils.polarToCartesian(24, 24, 16, (date.getSeconds() / 60) * 360);
        $rootScope.minutes_line = AuctionUtils.polarToCartesian(24, 24, 16, (date.getMinutes() / 60) * 360);
        $rootScope.hours_line = AuctionUtils.polarToCartesian(24, 24, 14, (date.getHours() / 12) * 360);
      }
    });

    /*      Kick client event    */
    $rootScope.$on('kick_client', function(event, client_id, msg) {
      $log.info({
        message: 'disable connection for client' + client_id
      });
      $rootScope.growlMessages.deleteMessage(msg);

      $http.post(base_url + '/kickclient', {
        'client_id': client_id,
      }).then(function(data) {
        $log.info({message: 'disable connection for client ' + client_id});
      });
    });
    //

    $rootScope.start_subscribe = function(argument) {
      $log.info({message: 'Start event source'});

      var response_timeout = $timeout(function() {
      $http.post(base_url + '/set_sse_timeout', {timeout: '7'}).then(function(data){
        $log.info({message: 'Handled set_sse_timeout on event source'});
      }, function(error){
        $log.error("Error on setting sse_timeout " + error);
      });
      $log.info({message: 'Start set_sse_timeout on event source', timeout: response_timeout});
      }, 20000);

      $rootScope.evtSrc = new EventSource(base_url + '/event_source', {withCredentials: true});
      $rootScope.restart_retries_events = 3;
      $rootScope.evtSrc.addEventListener('ClientsList', function(e) {
        var data = angular.fromJson(e.data);
        $log.info({message: 'Get Clients List', clients: data});

        $rootScope.$apply(function() {
          var i;
          if (angular.isObject($rootScope.clients)) {
            for (i in data) {
              if (!(i in $rootScope.clients)) {
                growl.warning($filter('translate')('In the room came a new user') + ' (IP:' + data[i].ip + ')' + '<button type="button" ng-click="$emit(\'kick_client\', \'' + i + '\', message )" class="btn btn-link">' + $filter('translate')('prohibit connection') + '</button>', {
                  ttl: 30000,
                  disableCountDown: true
                });
              }
            }
          }
          $rootScope.clients = data;
        });
      }, false);
      $rootScope.evtSrc.addEventListener('Tick', function(e) {
        $rootScope.restart_retries_events = 3;
        var data = angular.fromJson(e.data);
        $rootScope.last_sync = new Date(data.time);
        $log.debug({
          message: "Tick: " + data
        });
        if ($rootScope.auction_doc.current_stage > -1) {
          $rootScope.info_timer = AuctionUtils.prepare_info_timer_data($rootScope.last_sync, $rootScope.auction_doc, $rootScope.bidder_id, $rootScope.Rounds);
          $log.debug({
            message: "Info timer data",
            info_timer: $rootScope.info_timer
          });
          $rootScope.progres_timer = AuctionUtils.prepare_progress_timer_data($rootScope.last_sync, $rootScope.auction_doc);
          $log.debug({
            message: "Progres timer data",
            progress_timer: $rootScope.progres_timer
          });
        }

      }, false);
      $rootScope.evtSrc.addEventListener('Identification', function(e) {
        if (response_timeout) {
          $timeout.cancel(response_timeout);
        }
        var data = angular.fromJson(e.data);
        $log.info({message: "Get Identification", bidder_id: data.bidder_id, client_id: data.client_id});

        $rootScope.start_sync_event.resolve('start');
        $rootScope.$apply(function() {
          $rootScope.bidder_id = data.bidder_id;
          $rootScope.client_id = data.client_id;
          $rootScope.return_url = data.return_url;
          if ('coeficient' in data) {
            $rootScope.bidder_coeficient = math.fraction(data.coeficient);
            $log.info({message: "Get coeficient " + $rootScope.bidder_coeficient});
          }
        });
      }, false);

      $rootScope.evtSrc.addEventListener('RestoreBidAmount', function(e) {
        if (response_timeout) {
          $timeout.cancel(response_timeout);
        }
        var data = angular.fromJson(e.data);
        $log.debug({
          message: "RestoreBidAmount"
        });
        $rootScope.$apply(function() {
          $rootScope.form.bid = data.last_amount;
        });
      }, false);

      $rootScope.evtSrc.addEventListener('KickClient', function(e) {
        var data = angular.fromJson(e.data);
        $log.info({
          message: "Kicked"
        });
        window.location.replace(window.location.protocol + '//' + window.location.host + window.location.pathname + '/logout');
      }, false);
      $rootScope.evtSrc.addEventListener('Close', function(e) {
        $timeout.cancel(response_timeout);
        $log.info({
          message: "Handle close event source",
          error: e,
        });
        if (!$rootScope.follow_login_allowed) {
          growl.info($filter('translate')('You are an observer and cannot bid.'), {
            ttl: -1,
            disableCountDown: true
          }, 500);
          var params = AuctionUtils.parseQueryString(location.search);
          if (params.loggedin) {
            $timeout(function() {
              window.location.replace(window.location.protocol + '//' + window.location.host + window.location.pathname);
            }, 1000);
          }
        }
        $rootScope.start_sync_event.resolve('start');
        $rootScope.evtSrc.close();
      }, false);
      $rootScope.evtSrc.onerror = function(e) {
        $timeout.cancel(response_timeout);
        $log.error({
          message: "Handle event source error",
          error_data: e
        });
        $rootScope.restart_retries_events = $rootScope.restart_retries_events - 1;
        if ($rootScope.restart_retries_events === 0) {
          $rootScope.evtSrc.close();
          $log.info({
            message: "Handle event source stopped"
          });
          if (!$rootScope.follow_login_allowed) {
            growl.info($filter('translate')('You are an observer and cannot bid.'), {
              ttl: -1,
              disableCountDown: true
            });
          }
        }
        return true;
      };
    };
    $rootScope.changeLanguage = function(langKey) {
      $translate.use(langKey);
      $rootScope.lang = langKey;
    };
    // Bidding form msgs
    $rootScope.closeAlert = function(msg_id) {
      for (var i = 0; i < $rootScope.alerts.length; i++) {
        if ($rootScope.alerts[i].msg_id == msg_id) {
          $rootScope.alerts.splice(i, 1);
          return true;
        }
      }
    };
    $rootScope.auto_close_alert = function(msg_id) {
      $timeout(function() {
        $rootScope.closeAlert(msg_id);
      }, 4000);
    };
    $rootScope.get_round_number = function(pause_index) {
      return AuctionUtils.get_round_data(pause_index, $rootScope.auction_doc, $rootScope.Rounds);
    };
    $rootScope.show_bids_form = function(argument) {
      if ((angular.isNumber($rootScope.auction_doc.current_stage)) && ($rootScope.auction_doc.current_stage >= 0)) {
        if (($rootScope.auction_doc.stages[$rootScope.auction_doc.current_stage].type == 'bids') && ($rootScope.auction_doc.stages[$rootScope.auction_doc.current_stage].bidder_id == $rootScope.bidder_id)) {
          $log.info({
            message: "Allow view bid form"
          });
          $rootScope.max_bid_amount();
          $rootScope.view_bids_form = true;
          return $rootScope.view_bids_form;
        }
      }
      $rootScope.view_bids_form = false;
      return $rootScope.view_bids_form;
    };

    $rootScope.sync_times_with_server = function(start) {
      $http.get('/get_current_server_time', {
        'params': {
          '_nonce': Math.random().toString()
        }
      }).then(function(data) {
        $rootScope.last_sync = new Date(new Date(data.headers().date));
        $rootScope.info_timer = AuctionUtils.prepare_info_timer_data(
            $rootScope.last_sync,
            $rootScope.auction_doc,
            $rootScope.bidder_id,
            $rootScope.Rounds
        );
        $log.debug({
          message: "Info timer data:",
          info_timer: $rootScope.info_timer
        });
        $rootScope.progres_timer = AuctionUtils.prepare_progress_timer_data($rootScope.last_sync, $rootScope.auction_doc);
        $log.debug({
          message: "Progres timer data:",
          progress_timer: $rootScope.progres_timer
        });
        var params = AuctionUtils.parseQueryString(location.search);
        if ($rootScope.auction_doc.current_stage == -1) {
          if ($rootScope.progres_timer.countdown_seconds < 900) {
            $rootScope.start_changes_feed = true;
          } else {
            $timeout(function() {
              $rootScope.follow_login = true;
              $rootScope.start_changes_feed = true;
            }, ($rootScope.progres_timer.countdown_seconds - 900) * 1000);
          }
        }
        if ($rootScope.auction_doc.current_stage >= -1 && params.wait) {
          $rootScope.follow_login_allowed = true;
          if ($rootScope.progres_timer.countdown_seconds < 900) {
            $rootScope.follow_login = true;
          } else {
            $rootScope.follow_login = false;
            $timeout(function() {
              $rootScope.follow_login = true;
            }, ($rootScope.progres_timer.countdown_seconds - 900) * 1000);
          }
          $rootScope.login_params = params;
          delete $rootScope.login_params.wait;
          $rootScope.login_url =  base_url + '/login?' + AuctionUtils.stringifyQueryString($rootScope.login_params);
        } else {
          $rootScope.follow_login_allowed = false;
        }
      }, function(data, status, headers, config) {
        $log.error("get_current_server_time error");
      });
    };
    $rootScope.warning_post_bid = function(){
      growl.error('Unable to place a bid. Check that no more than 2 auctions are simultaneously opened in your browser.');
    };

    $rootScope.request_failed_warning = null;
    $rootScope.show_failed_request_warning = function(){
        if(!$rootScope.request_failed_warning){
            $rootScope.request_failed_warning = growl.error(
                "Your post bid request still hasn't succeed. Check (or change) your internet connection, browser or device.",
                {ttl: -1, disableCountDown: true}
            );
        }
    };
    $rootScope.request_failed_warning_timeout = null;
    $rootScope.schedule_failed_request_warning = function(){
        if (!$rootScope.request_failed_warning_timeout) {
            $rootScope.request_failed_warning_timeout = $timeout($rootScope.show_failed_request_warning, 5000);
        }
    };
    $rootScope.remove_failed_request_warning = function(){
        if($rootScope.request_failed_warning){
            $rootScope.growlMessages.deleteMessage(
                $rootScope.request_failed_warning
            );
            delete $rootScope.request_failed_warning;
        }
        if ($rootScope.request_failed_warning_timeout) {
            $timeout.cancel($rootScope.request_failed_warning_timeout);
            delete $rootScope.request_failed_warning_timeout;
        }
    };

    var too_low_bid_msg_id = "too_low_bid_msg_id";
    $rootScope.show_too_low_bid_warning = function(value){
        var prev_value = 0;
        if (angular.isObject($rootScope.auction_doc)) {
            var current_stage_obj = $rootScope.auction_doc.stages[$rootScope.auction_doc.current_stage];
            if (angular.isObject(current_stage_obj) && (current_stage_obj.amount || current_stage_obj.amount_features)) {
              if (($rootScope.auction_doc.auction_type || "default") === "meat") {
                if($rootScope.bidder_coeficient){
                    prev_value = math.fraction(current_stage_obj.amount_features) * $rootScope.bidder_coeficient;
                }
              } else {
                prev_value = math.fraction(current_stage_obj.amount);
              }
            }
        };
        var too_low_bid_ratio = prev_value !== 0 ? (100 - value / prev_value * 100).toFixed(2) : NaN;
        $rootScope.alerts.push({
            type: 'danger',
            msg: 'You are going to decrease your bid by {{too_low_bid_ratio}}%. Are you sure?',
            msg_vars: {too_low_bid_ratio: too_low_bid_ratio}
        });
    }
    $rootScope.prevent_sending_too_low_bid = function(value){
        var ratio = 1 - value / $rootScope.calculated_max_bid_amount;
        if (
            $rootScope.calculated_max_bid_amount == null || value == null || value === -1
            || ratio < 0.3
            || $rootScope.force_post_low_bid === value
        ) {
            $rootScope.force_post_low_bid = undefined;
            $rootScope.closeAlert(too_low_bid_msg_id);
            return false;
        } else {
            $rootScope.force_post_low_bid = value;
            $rootScope.show_too_low_bid_warning(value);
            return true;
        }
    };
    $rootScope.post_bid = function(bid) {
      $log.info({
        message: "Start post bid",
        bid_data: parseFloat(bid) || parseFloat($rootScope.form.bid) || 0
      });

      if (parseFloat($rootScope.form.bid) == -1) {
        var msg_id = Math.random();
        $rootScope.alerts.push({
          msg_id: msg_id,
          type: 'danger',
          msg: 'To low value'
        });
        $rootScope.auto_close_alert(msg_id);
        return 0;
      }
      if ($rootScope.form.BidsForm.$valid) {
        $rootScope.alerts = [];
        var bid_amount = parseFloat(bid) || parseFloat($rootScope.form.bid) || 0;
        if ($rootScope.prevent_sending_too_low_bid(bid_amount)){
            return 0;
        }
        if (bid_amount == $rootScope.minimal_bid.amount) {
          var msg_id = Math.random();
          $rootScope.alerts.push({
            msg_id: msg_id,
            type: 'warning',
            msg: 'The proposal you have submitted coincides with a proposal of the other participant. His proposal will be considered first, since it has been submitted earlier.'
          });
        }
        $rootScope.form.active = true;
        $timeout(function() {
          $rootScope.form.active = false;
        }, 5000);
        if (!$rootScope.post_bid_timeout) {
          $rootScope.post_bid_timeout = $timeout($rootScope.warning_post_bid, 10000);
        }
        $rootScope.schedule_failed_request_warning();

        $http.post(base_url + '/postbid', {
          'bid': parseFloat(bid) || parseFloat($rootScope.form.bid) || 0,
          'bidder_id': $rootScope.bidder_id || bidder_id || "0"
        }).then(function(success) {
          $rootScope.remove_failed_request_warning();
          if ($rootScope.post_bid_timeout){
            $timeout.cancel($rootScope.post_bid_timeout);
            delete $rootScope.post_bid_timeout;
          }
          $rootScope.form.active = false;
          var msg_id = '';
          if (success.data.status == 'failed') {
            for (var error_id in success.data.errors) {
              for (var i in success.data.errors[error_id]) {
                msg_id = Math.random();
                $rootScope.alerts.push({
                  msg_id: msg_id,
                  type: 'danger',
                  msg: success.data.errors[error_id][i]
                });
                $log.info({
                  message: "Handle failed response on post bid",
                  bid_data: success.data.errors[error_id][i]
                });
                $rootScope.auto_close_alert(msg_id);
              }
            }
          } else {
            var bid = success.data.data.bid;
            var msg_id = Math.random();
            if (bid == -1) {
              $rootScope.alerts = [];
              $rootScope.allow_bidding = true;
              $log.info({
                message: "Handle cancel bid response on post bid"
              });
              $rootScope.alerts.push({
                msg_id: msg_id,
                type: 'success',
                msg: 'Bid canceled'
              });
              $log.info({
                message: "Handle cancel bid response on post bid"
              });
              $rootScope.form.bid = "";
              $rootScope.form.full_price = '';
            } else {
              $log.info({
                message: "Handle success response on post bid",
                bid_data: bid
              });
              $rootScope.alerts.push({
                msg_id: msg_id,
                type: 'success',
                msg: 'Bid placed'
              });
              $rootScope.allow_bidding = false;
            }
            $rootScope.auto_close_alert(msg_id);
          }
        }, function(error) {
            $log.info({
              message: "Handle error on post bid",
              bid_data: error.status
            });
            if ($rootScope.post_bid_timeout){
              $timeout.cancel($rootScope.post_bid_timeout);
              delete $rootScope.post_bid_timeout;
            }
            if (error.status == 401) {
              $rootScope.remove_failed_request_warning();
              $rootScope.alerts.push({
                msg_id: Math.random(),
                type: 'danger',
                msg: 'Ability to submit bids has been lost. Wait until page reloads, and retry.'
              });
              $log.error({
                message: "Ability to submit bids has been lost. Wait until page reloads, and retry."
              });
              relogin = function() {
                window.location.replace(window.location.href + '/relogin?amount=' + $rootScope.form.bid);
              }
              $timeout(relogin, 3000);
            } else {
              $log.error({
                message: "Unhandled Error while post bid",
                error_data: error.data
              });
              $timeout($rootScope.post_bid, 2000);
            }
          });
      }
    };
    $rootScope.edit_bid = function() {
      $rootScope.allow_bidding = true;
    };
    $rootScope.max_bid_amount = function() {
      var amount = 0;
      if ((angular.isString($rootScope.bidder_id)) && (angular.isObject($rootScope.auction_doc))) {
        var current_stage_obj = $rootScope.auction_doc.stages[$rootScope.auction_doc.current_stage] || null;
        if ((angular.isObject(current_stage_obj)) && (current_stage_obj.amount || current_stage_obj.amount_features)) {
          if ($rootScope.bidder_coeficient && ($rootScope.auction_doc.auction_type || "default" == "meat")) {
            amount = math.fraction(current_stage_obj.amount_features) * $rootScope.bidder_coeficient - math.fraction($rootScope.auction_doc.minimalStep.amount);
          } else {
            amount = math.fraction(current_stage_obj.amount) - math.fraction($rootScope.auction_doc.minimalStep.amount);
          }
        }
      };
      if (amount < 0) {
        $rootScope.calculated_max_bid_amount = 0;
        return 0;
      }
      $rootScope.calculated_max_bid_amount = amount;
      return amount;
    };
    $rootScope.calculate_minimal_bid_amount = function() {
      if ((angular.isObject($rootScope.auction_doc)) && (angular.isArray($rootScope.auction_doc.stages)) && (angular.isArray($rootScope.auction_doc.initial_bids))) {
        var bids = [];
        var filter_func;
        if ($rootScope.auction_doc.auction_type == 'meat') {
          filter_func = function(item, index) {
            if (!angular.isUndefined(item.amount_features)) {
              bids.push(item);
            }
          };
        } else {
          filter_func = function(item, index) {
            if (!angular.isUndefined(item.amount)) {
              bids.push(item);
            }
          };
        }
        $rootScope.auction_doc.stages.forEach(filter_func);
        $rootScope.auction_doc.initial_bids.forEach(filter_func);
        $rootScope.minimal_bid = bids.sort(function(a, b) {
          if ($rootScope.auction_doc.auction_type == 'meat') {
            var diff = math.fraction(a.amount_features) - math.fraction(b.amount_features);
          } else {
            var diff = a.amount - b.amount;
          }
          if (diff == 0) {
            return Date.parse(a.time || "") - Date.parse(b.time || "");
          }
          return diff;
        })[0];
      }
    };
    $rootScope.start_sync = function() {
        $http.get(
            '/api/auctions/' + AuctionConfig.auction_doc_id,
            {
                'params': {
                  '_nonce': Math.random().toString()
                }
            }
        ).then(
            function(response) {
                var doc = response.data;
                $rootScope.restart_retries = AuctionConfig.restart_retries;
                $rootScope.replace_document(doc);
                $timeout(function() {
                    $rootScope.start_sync();
                }, 5000);
            },
            function(response){
                $log.error({
                  message: "Changes error",
                  error_data: {"code": response.status, "data": response.data}
                });
                $timeout(function() {
                  if ($rootScope.restart_retries != AuctionConfig.restart_retries) {
                    growl.warning('Internet connection is lost. Attempt to restart after 1 sec', {
                      ttl: 1000
                    });
                  }
                  $rootScope.restart_retries -= 1;
                  if ($rootScope.restart_retries) {
                      $log.debug({message: 'Restart feed pooling...'});
                      $timeout(function() {
                        $rootScope.start_sync();
                      }, 1000);
                  } else {
                    growl.error('Synchronization failed');
                    $log.error({message: 'Synchronization failed'});
                  }
                }, 1000);
            }
        );
    };

    // HERE
    $rootScope.start = function() {
        $http.get('/api/auctions/' + AuctionConfig.auction_doc_id).then(
            function(response) {
                var doc = response.data;
                if (doc.procurementMethodType === 'esco') {
                    $log.error({message: 'Please use the correct link to view the auction'});
                    $rootScope.document_not_found = true;
                    var msg_correct_link = $filter('translate')('Please use the correct link to view the auction.');
                    document.body.insertAdjacentHTML(
                        'afterbegin',
                        '<div class="container alert alert-danger" role="alert">' + msg_correct_link +'</div>'
                    );
                } else {
                      $rootScope.http_error_timeout = $rootScope.default_http_error_timeout;
                      var params = AuctionUtils.parseQueryString(location.search);

                      $rootScope.start_sync_event = $q.defer();
                      if (doc.current_stage >= -1 && params.wait) {
                        $log.info("login allowed " + doc.current_stage);
                        $rootScope.follow_login_allowed = true;
                        $log.info({message: 'client wait for login'});
                      } else {
                        $rootScope.follow_login_allowed = false;
                      }
                      $rootScope.title_ending = AuctionUtils.prepare_title_ending_data(doc, $rootScope.lang);
                      $rootScope.replace_document(doc);
                      $rootScope.document_exists = true;
                      if (AuctionUtils.UnsupportedBrowser()) {
                        $timeout(function() {
                          $rootScope.unsupported_browser = true;
                          growl.error($filter('translate')('Your browser is out of date, and this site may not work properly.') + '<a style="color: rgb(234, 4, 4); text-decoration: underline;" href="http://browser-update.org/uk/update.html">' + $filter('translate')('Learn how to update your browser.') + '</a>', {
                            ttl: -1,
                            disableCountDown: true
                          });
                        }, 500);
                      };
                      $rootScope.scroll_to_stage();
                      if ($rootScope.auction_doc.current_stage != ($rootScope.auction_doc.stages.length - 1)) {
                        if ($cookieStore.get('auctions_loggedin')||AuctionUtils.detectIE()) {
                          $log.info({
                            message: 'Start private session'
                          });
                          $rootScope.start_subscribe();

                        } else {
                          $log.info({
                            message: 'Start anonymous session'
                          });

                          if ($rootScope.auction_doc.current_stage == - 1){
                            $rootScope.$watch('start_changes_feed', function(newValue, oldValue){
                              if(newValue && !($rootScope.sync)){
                                $log.info({
                                  message: 'Start changes feed'
                                });
                                $rootScope.sync = $rootScope.start_sync();
                              }
                            });
                          } else {
                            $rootScope.start_sync_event.resolve('start');
                          }
                          $log.info("LOGIN ALLOWED " + $rootScope.follow_login_allowed);
                          if (!$rootScope.follow_login_allowed) {
                            $timeout(function() {
                              growl.info($filter('translate')('You are an observer and cannot bid.'), {
                                ttl: -1,
                                disableCountDown: true
                              });
                            }, 500);
                          }
                        }
                        $rootScope.restart_retries = AuctionConfig.restart_retries;
                        $rootScope.start_sync_event.promise.then(function() {
                          $rootScope.sync = $rootScope.start_sync();
                        });
                      } else {
                        // TODO: CLEAR COOKIE
                        $log.info({
                          message: 'Auction ends already'
                        });
                      }
                    }

            },
            function(response) {
                if (response.status == 404) {
                    $log.error({message: 'Not Found Error', error_data: response});
                    $rootScope.document_not_found = true;
                } else {
                    $log.error({ message: 'Server Error', error_data: err});
                    $rootScope.http_error_timeout = $rootScope.http_error_timeout * 2;
                    $timeout(
                        $rootScope.start,
                        $rootScope.http_error_timeout
                    );
                }
            }
        );
    };
    $rootScope.replace_document = function(new_doc) {
      if ($rootScope.auction_doc && $rootScope.auction_doc.modified == new_doc.modified) return;

      if ((angular.isUndefined($rootScope.auction_doc)) || (new_doc.current_stage - $rootScope.auction_doc.current_stage === 0) || (new_doc.current_stage === -1)) {
        if (angular.isUndefined($rootScope.auction_doc)) {
          $log.info({
            message: 'Change current_stage',
            current_stage: new_doc.current_stage,
            stages: (new_doc.stages || []).length - 1
          });
        }
      } else {
        $log.info({
          message: 'Change current_stage',
          current_stage: new_doc.current_stage,
          stages: (new_doc.stages || []).length - 1
        });
        $rootScope.form.bid = null;
        $rootScope.allow_bidding = true;
      }
      $rootScope.auction_doc = new_doc;
      $rootScope.sync_times_with_server();
      $rootScope.calculate_rounds();
      $rootScope.calculate_minimal_bid_amount();
      $rootScope.scroll_to_stage();
      $rootScope.show_bids_form();
      if(!$rootScope.$$phase) {
        $rootScope.$apply();
      }
    };
    $rootScope.calculate_rounds = function(argument) {
      $rootScope.Rounds = [];
      $rootScope.auction_doc.stages.forEach(function(item, index) {
        if (item.type == 'pause') {
          $rootScope.Rounds.push(index);
        }
      });
    };
    $rootScope.scroll_to_stage = function() {
      AuctionUtils.scroll_to_stage($rootScope.auction_doc, $rootScope.Rounds);
    };
    $rootScope.array = function(int) {
      return new Array(int);
    };
    $rootScope.open_menu = function() {
      var modalInstance = $aside.open({
        templateUrl: 'templates/menu.html',
        size: 'lg',
        backdrop: true
      });
    };
    /* 2-WAY INPUT */
    $rootScope.calculate_bid_temp = function() {
      var new_full_price;
      if(angular.isDefined($rootScope.form.bid)){
        var form_bid = Number(math.fraction(($rootScope.form.bid * 100).toFixed(), 100));
        new_full_price = form_bid / $rootScope.bidder_coeficient;
      }
      $rootScope.form.full_price = new_full_price;
    };
    $rootScope.calculate_full_price_temp = function() {
      var new_form_bid;
      if(angular.isDefined($rootScope.form.full_price)){
        new_form_bid = (math.fix((math.fraction($rootScope.form.full_price) * $rootScope.bidder_coeficient) * 100)) / 100;
      }
      $rootScope.form.bid = new_form_bid;
    };
    $rootScope.start();
}]);