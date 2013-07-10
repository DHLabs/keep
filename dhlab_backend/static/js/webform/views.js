var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['jquery', 'vendor/underscore', 'vendor/backbone-min', 'vendor/forms/backbone-forms.min', 'models', 'builder', 'constraints'], function($, _, Backbone, Forms, xFormModel, build_form, XFormConstraintChecker) {
  var xFormView, _ref;
  xFormView = (function(_super) {
    __extends(xFormView, _super);
 
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

      if (this._active_question().info.bind && this._active_question().info.bind.map) {
        _geopointDisplay();        
      }

      return this;
    };

    _geopointDisplay = function() {
      var map;
      question = ($('.active').data('key'));
      var element = document.getElementById(question + "_map");
      if(!(element.classList.contains('map'))) {
        element.classList.add('map');
        map = L.map((question + '_map'), {
          center: [36.60, -120.65],
          zoom: 5});
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
          maxZoom: 18,
          reuseTiles: true
        }).addTo(map);
      };
      var popup = L.popup();
      function onMapClick(e) {
        popup
          .setLatLng(e.latlng)
          .setContent("Latitude and Longitude: " + e.latlng.toString())
          .openOn(map);
        $("#" + question).val(e.latlng.lat + " " + e.latlng.lng + " 0 0");
      }
      map.on('click', onMapClick);
      map.invalidateSize(false);
    };


    // For calculations.  Currently only supporting basic -, +, *, div
    _performCalcluate = function(equation) {
      var evaluation, i, begin, end, side1, side2, operation, parenCount;
      parenCount = 0;

      // Initial paren finder and recursion to get to the start of the equation
      for (i = 0; i < equation.length; i++) {
        if (equation[i] === '(') {
          if (parenCount === 0) {
            begin = i;
          }
          parenCount++;
        } else if (equation[i] === ')') {
          parenCount--;
          if (parenCount === 0) {
            end = i;
            equation = equation.replace( equation.substring(begin, end + 1), _performCalcluate(equation.substring(begin + 1, end)) );
          }
        };
      };

      side1 = equation.slice(0, equation.indexOf(' ') );
      operation = equation.slice(side1.length + 1, equation.lastIndexOf(' ') );
      side2 = equation.slice(equation.lastIndexOf(' ') + 1);
      if ( side1.slice(0, 2) === '${' ) {
        side1 = $('#' + side1.slice(2, -1)).val();
      };
      if ( side2.slice(0, 2) === '${' ) {
        side2 = $('#' + side2.slice(2, -1)).val();
      };
      if ( operation === '-' ) {
        return (side1 - side2);
      }
      else if ( operation === '+' ) {
        return (side1 + side2);
      }
      else if ( operation === '*' ) {
        return (side1 * side2);
      }
      else if ( operation === 'div' ) {
        return (side1 / side2);
      }
      else {
        return;
      };
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
      
      if (question.info.bind && (question.info.bind.required === true || question.info.bind.required === 'yes')) {
        if (this.renderedForm.getValue()[question.key].length === 0) {
          $("#alert-placeholder").html('<div class="alert alert-error"><a class="close" data-dismiss="alert">x</a><span>Answer is required.</span></div>');
          return false;
        }
      }
      if (!XFormConstraintChecker.passesConstraint(question.info, this.renderedForm.getValue())) {
        $("#alert-placeholder").html('<div class="alert alert-error"><a class="close" data-dismiss="alert">x</a><span>Answer doesn\'t pass constraint:' + question.info.bind.constraint + '</span></div>');
        return false;
      }
      return true;
    };

    xFormView.prototype.switch_question = function(element, forward) {
      var current_question, form_info, question_index, switch_question, switch_question_key, switch_question_idx, switch_question_info, current_question_idx, current_question_info;
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

      if ((form_info.bind && form_info.bind.calculate) || !XFormConstraintChecker.isRelevant(form_info, this.renderedForm.getValue()))  {
        if (form_info.bind && form_info.bind.calculate) {
          $('#' + form_info.name).val(_performCalcluate(form_info.bind.calculate));
        }
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
      
      $('.active').fadeOut(1);
      $('.alert').fadeOut(1);
      $('.active').removeClass('active');

      // Group controls
      if (form_info.control) {
        if (form_info.control.appearance && form_info.control.appearance === 'field-list') {
          var current_tree = form_info.tree;

          $('#' + switch_question_key + "_field").addClass('active');
          switch_question_idx = question_index + 1;
          switch_question_info = this.input_fields[switch_question_idx];

          while (switch_question_info.tree === current_tree) {
            switch_question = $("#" + $($('.control-group').eq(switch_question_idx)[0]).data('key') + "_field");
            switch_question.fadeIn(1).addClass('active');
            $('.active input').focus()
            if ((switch_question_idx + 1) < this.input_fields.length) {
              switch_question_idx += 1;
              switch_question_info = this.input_fields[switch_question_idx];
            }
          }
        }
      } else {
        while (this.input_fields[question_index].bind && this.input_fields[question_index].bind.group_start) {
          if (forward) {
            if (question_index < this.input_fields.length) {
              question_index += 1;
            }
          } else {
            if (question_index > 0) {
              question_index -= 1;
            }
          }
        }
        switch_question = $('#' + $($('.control-group').eq(question_index)[0]).data('key') + "_field");
        form_info = this.input_fields[question_index];
        var subsequent;
        if ((subsequent = form_info.title.indexOf("${")) !== -1 ) {
          var end_subsequent = form_info.title.indexOf("}", subsequent);
          var subsequent_st = form_info.title.substring(subsequent + 2, end_subsequent);
          switch_question[0].innerHTML = switch_question[0].innerHTML.replace(/\${.+}/, $("#" + subsequent_st).val());
        };
        switch_question.fadeIn(1).addClass('active');
      };
      if(form_info.bind && form_info.bind.map){
        _geopointDisplay();
      };
      //if (form_info.bind && form_info.bind.calculation) {
      //  _performCalcluate(this._active_question());
      //  this.switch_question($('.control-group').eq(question_index), forward);
      //}
      //if (this.input_fields[question_index])

      /** For later use, not working as of 9 July 2013
      if( this.input_fields[question_index].options) {
        var i;
        for ( i=0; i < this.input_fields[question_index].options.length; i++ ) {
          if ( this.input_fields[question_index].options[i].val === 'other' ) {
            _specifiedOther(this._active_question());
          } 
        }
      }
      **/

      this._display_form_buttons(question_index);
      return this;
    };

    xFormView.prototype.next_question = function() {
      var question, question_index;
      question = this._active_question();
      question_index = question.idx;
      if (question.info.control && question.info.control.appearance === 'field-list') {
        var current_tree = question.info.tree;
        question_index += 1;
        while (this.input_fields[question_index].tree === current_tree) {
          question_index += 1;
        }
      } else if (question_index < this.input_fields.length) {
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
      var current_tree = this.input_fields[question_index - 1].tree;
      if (current_tree != "/") {
        var temp_idx = question_index - 1;
        while (this.input_fields[temp_idx].tree === current_tree) {
          temp_idx -= 1;
        }
        temp_idx += 1;
        if (this.input_fields[temp_idx].control && this.input_fields[temp_idx].control.appearance === 'field-list') {
          question_index = temp_idx;
        } else {
          question_index -= 1;
        };
      } else {
        question_index -= 1;
      };
      this.switch_question($('.control-group').eq(question_index)[0], false);
      return this;
    };

    return xFormView;

  })(Backbone.View);
  return xFormView;
});