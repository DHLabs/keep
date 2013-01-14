
$(function(){

  var mobileView = false;

  var getForm;
  var _fieldsets = [];
  var _schema = {};
  var _data = {};
  var item_dict = {};
  var swipeFrame;

  var xFormModel = Backbone.Model.extend();

  var xFormView = Backbone.View.extend({

    el:       $("#xform_view"),
    model:    new xFormModel(),

    initialize: function() {

      // Begin render when the model is finishing fetching from the server
      this.listenTo( this.model, 'change', this.render );
      this.model.fetch({ url: "/api/v1/forms/50ca6a9ca14cd282229139fa/?user=admin&key=c308c86bd454486273a603b573de4342&format=json"});

    },

    render: function() {

      if( mobileView ) {

        this.loadMobileForm();

      } else {

        this.loadForm();

      }

      return this;

    },

    recursiveAdd: function(child_obj) {
        var self  = this;
        var child = child_obj;

        schema_dict = {};

        if( child.type =='string' || child.type == 'text' ) {

          schema_dict['type'] = 'Text';
          // schema_dict['element'] = child.name;
          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;
          // console.log(schema_dict);

          if(_fieldsets.length === 0 && mobileView) {
            schema_dict['template'] = 'firstField';
          }

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else if(child.type =='int' || child.type == 'integer') {

          schema_dict['type'] = 'Number';
          // schema_dict['element'] = child.name;
          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;
          // console.log(schema_dict);

          if(_fieldsets.length === 0  && mobileView) {
            schema_dict['template'] = 'firstField';
          }

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else if(child.type =='decimal') {

          schema_dict['type'] = 'Number';
          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;

          if(_fieldsets.length === 0 && mobileView) {
            schema_dict['template'] = 'firstField';
          }

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else if(child.type =='date') {

          schema_dict['type'] = 'Date';
          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else if(child.type =='today') {

          schema_dict['type'] = 'Date';
          schema_dict['help'] = child.hint;
          schema_dict['title'] = 'Today';

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else if(child.type =='time') {

          schema_dict['type'] = 'DateTime';

          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else if(child.type =='trigger') {

          schema_dict['type'] = 'Checkbox';

          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;

          item_dict[child.name] = schema_dict;

          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else if(child.type =='note') {

          schema_dict['type'] = 'Text';

          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;
          schema_dict['template'] = 'noteField';

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else if(child.type =='dateTime') {

          schema_dict['type'] = 'DateTime';

          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else if(child.type =='select all that apply') {

          schema_dict['type'] = 'Checkboxes';
          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;

          option_array = [];

          _.each(child.children, function(option){

              option_dict = {};
              option_dict['val'] = option.name;
              option_dict['label'] = option.label;

              option_array.push(option_dict);
          });

          // console.log(option_array);
          schema_dict['options'] = option_array;

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else if(child.type =='group') {

          // this is a hack
          schema_dict['type'] = 'Text';
          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;
          schema_dict['template'] = 'groupBegin';

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _.each(child.children, function(_child){
              self.recursiveAdd(_child);
          });


          schema_dict = {};
          schema_dict['type'] = 'Text';
          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;
          schema_dict['template'] = 'groupEnd';

          item_dict[child.name + '-end'] = schema_dict;
          _fieldsets.push(child.name + '-end');

        } else if(child.type =='select one') {

          schema_dict['type'] = 'Select';
          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.label;

          option_array = [];

          _.each(child.children, function(option){

              option_dict = {};
              option_dict['val'] = option.name;
              option_dict['label'] = option.label;

              option_array.push(option_dict);
          });


          // console.log(option_array);
          schema_dict['options'] = option_array;

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

          _data[child.name] = child.default;

        } else {

          schema_dict['type'] = 'Text';
          schema_dict['help'] = child.hint;
          schema_dict['title'] = child.type;
          schema_dict['template'] = 'unsupportedField';

          item_dict[child.name] = schema_dict;
          _fieldsets.push(child.name);

        }

    },

    loadMobileForm: function() {

      _fieldsets = [];
      _schema = {};
      _data = {};
      item_dict = {};
      swipeFrame = null;

      $('.dropdown-toggle').dropdown('toggle');

      console.log(this.model.get('formTitle'));

      var xform_json = this.model.get('jsonString');
      var xformObj = $.parseJSON(xform_json);

      $(document).bind(
        'touchmove',
        function(e) {
          e.preventDefault();
        }
      );

      Backbone.Form.setTemplates({
        fieldset: '<ul>{{fields}}</ul',
        customForm: '<div id="slider2" class="swipe">{{fieldsets}}</div>',
        field: '<li style="display:none;"><label for="{{id}}">{{title}}</label><div>{{editor}}</div><div>{{help}}</div></li>',
        unsupportedField: '<li style="display:none;"><label for="{{id}}">{{title}}</label></li>',
        firstField: '<li style="display:block;"><label for="{{id}}">{{title}}</label><div>{{editor}}</div><div>{{help}}</div></li>',
        noteField: '<li style="display:none;"><label class="control-label" for="{{id}}">{{title}}</label></div></li>',
        groupBegin: '<li style="display:none;"><div class="well"><div><strong>Group: </strong>{{title}}</div></div></li>',
        groupEnd: '<li style="display:none;"><div><strong>Group End: </strong>{{title}}<hr></div></li>'
      });

      var self = this;
      _.each(xformObj.children, function(child) {

        self.recursiveAdd(child);

      });

      getForm = new Backbone.Form({
        template: 'customForm',
        schema: item_dict,
        data: _data,
        fields: _fieldsets

      }).render();

      $('#formDiv').html("");
      $('#formDiv').html(getForm.el);

      swipeFrame = new Swipe(document.getElementById('slider2'));
      console.log(swipeFrame);
    },


    loadForm: function() {

      _fieldsets = [];
      _schema = {};
      _data = {};
      item_dict = {};
      swipeFrame = null;

      $('.dropdown-toggle').dropdown('toggle');

      Backbone.Form.setTemplates({
        unsupportedField: '<div><label for="{{id}}"><strong>Unsupported:</strong> {{title}}</label></div>',
        noteField: '<div><strong>Note: </strong>{{title}}</div>',
        groupBegin: '<div class="well"><div><strong>Group: </strong>{{title}}</div></div>',
        groupEnd: '<div><hr></div>'
      });

      var self = this;
      _.each( this.model.attributes.children, function(child) {

        self.recursiveAdd(child);

      });


      getForm = new Backbone.Form({

        schema: item_dict,
        data: _data,
        fields: _fieldsets

      }).render();

      $('#formDiv').html("");
      $('#formDiv').html(getForm.el);

    }

  });

  var App = new xFormView();

});
