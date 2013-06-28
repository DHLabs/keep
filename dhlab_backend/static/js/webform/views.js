var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['jquery', 'vendor/underscore', 'vendor/backbone-min', 'vendor/forms/backbone-forms.min', 'models', 'builder', 'constraints'], function($, _, Backbone, Forms, xFormModel, build_form, XFormConstraintChecker) {
  var xFormView, _ref;
  xFormView = (function(_super) {
    __extends(xFormView, _super);

    var current_tree;

    function xFormView() {
      _ref = xFormView.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    xFormView.prototype.el = $('#webform');

    xFormView.prototype.model = new xFormModel();

    xFormView.prototype.events = {
      'click #submit_btn': 'submit',
      'click #form_sidebar > li': 'switch_question',
      'click #next_btn': 'next_question',
      'click #prev_btn': 'prev_question'
    };

    xFormView.prototype._fieldsets = [];

    xFormView.prototype._data = [];

    xFormView.prototype._schema = {};

    xFormView.prototype.item_dict = {};

    xFormView.prototype.input_fields = [];

    xFormView.prototype.renderedForm = null;

    xFormView.prototype.languages = [];

    xFormView.prototype.initialize = function() {
      this.form_id = $('#form_id').html();
      this.user = $('#user').html();
      this.listenTo(this.model, 'change', this.render);
      this.model.fetch({
        url: "/api/v1/repos/" + this.form_id + "/?user=" + this.user + "&format=json"
      });
      return this;
    };

    xFormView.prototype.submit = function() {
      return $(this.renderedForm.el).submit();
    };

    xFormView.prototype.recursiveAdd = build_form;

    xFormView.prototype.render = function() {
      var submitChild,
        _this = this;
      submitChild = {
        bind: {
          readonly: "true()"
        },
        label: "Form Complete!  Click Submit, or hit Previous to review your answers.",
        name: "knozr563kj04tyn748945",
        type: "note"
      };
      this.model.attributes.children.push(submitChild);
      _.each(this.model.attributes.children, function(child) {
        return _this.recursiveAdd(child, "/", _this.model.attributes.default_language);
      });
      this.renderedForm = new Backbone.Form({
        schema: this.item_dict,
        data: this._data,
        fields: this._fieldsets
      }).render();

      _.each(this.item_dict, function(child, key) {
        child.name = key;

        return _this.input_fields.push(child);
      });
      $('#formDiv').html(this.renderedForm.el);
      $('.control-group').first().show().addClass('active');
      $('.active input').focus();
      this._display_form_buttons(0);

      this.current_tree = (this._active_question().info.tree);
      console.log(this.current_tree);
      // TODO: Fix edge case of map being first question, 
      // if geopoint is the first question, the map doesn't show

      return this;
    };

    _geopointDisplay = function(map) {
      var map;
      if(map === undefined) {
        map = L.map('map', {
          center: [36.60, -120.65],
          zoom: 10});
      }
      L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
        rehuseTiles: true
      }).addTo(map);

      var popup = L.popup();
      function onMapClick(e) {
        popup
          .setLatLng(e.latlng)
          .setContent("Latitude and Longitude: " + e.latlng.toString())
          .openOn(map);
        question = ($('.active').data('key'));
        $("#" + question).val(e.latlng.lat + " " + e.latlng.lng + " 0 0");
      }
      map.on('click', onMapClick);
    };

    xFormView.prototype._display_form_buttons = function(question_index) {
      if (question_index === this.input_fields.length - 1) {
        $('#prev_btn').show();
        $('#submit_btn').show();
        $('#next_btn').hide();
        $('#xform_view').keydown (function(e) {
          if (e.keyCode === 13) {
            $('#submit_btn').click();
          }
        })
      } else if (question_index === 0) {
        $('#prev_btn').hide();
        $('#submit_btn').hide();
        $('#next_btn').show();
        $('#xform_view').keydown (function(e) {
          if (e.keyCode === 13) {
            $('#next_btn').click();
          }
        })
      } else {
        $('#prev_btn').show();
        $('#next_btn').show();
        $('#submit_btn').hide();
        $('#xform_view').keydown (function(e) {
          if (e.keyCode === 13) {
            $('#next_btn').click();
          }
        })
      }
      return this;
    };

    xFormView.prototype._active_question = function() {
      var form_info, question, question_index;
      question = $('.active').data('key');
      question_index = -1;
      form_info = _.find(this.input_fields, function(child) {
        question_index += 1;
        return child.name === question;
      });
      return {
        'key': question,
        'idx': question_index,
        'info': form_info
      };
    };

    xFormView.prototype.passes_question_constraints = function() {
      var question;
      question = this._active_question();
      if (question.info.bind && question.info.bind.required === "yes") {
        if (this.renderedForm.getValue()[question.key].length === 0) {
          alert("Answer is required");
          return false;
        }
      }
      if (!XFormConstraintChecker.passesConstraint(question.info, this.renderedForm.getValue())) {
        alert("Answer doesn't pass constraint:" + question.info.bind.constraint);
        return false;
      }
      return true;
    };

    xFormView.prototype.switch_question = function(element, forward) {
      var current_question, form_info, question_index, switch_question, switch_question_key, current_question_info;
      if (forward) {
        if (!this.passes_question_constraints()) {
          return this;
        }
      }
      current_question = this._active_question();
      switch_question_key = $(element).data('key');
      question_index = -1;
      form_info = _.find(this.input_fields, function(child) {
        question_index += 1;
        return child.name === switch_question_key;
      });

      if (!XFormConstraintChecker.isRelevant(form_info, this.renderedForm.getValue()) || (form_info.tree != "/" && form_info.tree === this.current_tree)) {
        if (forward) {
          if (question_index < this.input_fields.length) {
            question_index += 1;
          }
        } else {
          if (question_index > 0) {
            question_index -= 1;
          }
        }

        this.switch_question($('.control-group').eq(question_index), forward);
        return;
      }

      
      current_question_info = current_question.info;
      current_question_idx = current_question.idx;

      $('.active').removeClass('active');

      console.log(current_question_info.tree);
      while (current_question_info.tree === this.current_tree) {
        current_question = $("#" + $($('.control-group').eq(current_question_idx)[0]).data('key') + "_field");
        current_question.fadeOut('slow');
        if ((current_question_idx + 1) < this.input_fields.length) { 
          current_question_idx += 1;
          current_question_info = this.input_fields[current_question_idx];
        }
        else { break; };
        if (current_question_info.tree === '/') {
          break;
        }
      };

      this.current_tree = form_info.tree;
      console.log(switch_question_key)
      switch_question = $("#" + switch_question_key + "_field");
      switch_question.fadeIn('slow').addClass('active');
      $('.active input').focus();
      
      //current_question.fadeOut('fast', function() {
      //  switch_question.fadeIn('fast').addClass('active');
        
      //  return $('.active input').focus();
      //});
      if(form_info.bind != undefined && form_info.bind.map != undefined){
        _geopointDisplay();
      };
      this._display_form_buttons(question_index);
      return this;
    };

    xFormView.prototype.next_question = function() {
      var question, question_index;
      question = this._active_question();
      question_index = question.idx;
      if (question_index < this.input_fields.length) {
        question_index += 1;
      }
      this.switch_question($('.control-group').eq(question_index)[0], true);
      return this;
    };

    xFormView.prototype.prev_question = function() {
      var question, question_index;
      question = this._active_question();
      question_index = question.idx;
      if (question_index <= 0) {
        return this;
      }
      question_index -= 1;
      this.switch_question($('.control-group').eq(question_index)[0], false);
      return this;
    };

    return xFormView;

  })(Backbone.View);
  return xFormView;
});