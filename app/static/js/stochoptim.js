
$( document ).ready( function() {
    //loadTemplate("speciesEditorTemplate", "/model/speciesEditor.html");
    //loadTemplate("parameterEditorTemplate", "/model/parameterEditor.html");
    //loadTemplate("reactionEditorTemplate", "/model/reactionEditor.html");

    waitForTemplates(run);
});

//Get and check inputs
var checkAndGet = function(selectTable)
{
    var jobName = $( "#jobName" ).val().trim();

    if(!/^[a-zA-Z_][a-zA-Z0-9_]+$/.test(jobName))
    {
        updateMsg( { status : false,
                     msg : "Job name must be letters (a-z and A-Z), underscores, and numbers only, and start with a letter or an underscore" } );
        return false;
    }

    var execType = $( "input:radio[name=exec_type]:checked" ).val();

    var crossEntropyStep = $( "#crossEntropyStep" ).prop('checked');
    var emStep = $( "#emStep" ).prop('checked');
    var uncertaintyStep = $( "#uncertaintyStep" ).prop('checked');

    var seed = $( "#seed" ).val();

    if(!/^[0-9]+$/.test(seed))
    {
        updateMsg( { status : false,
                     msg : "Seed must be an integer" } );
        return false;
    }

    seed = parseInt(seed);

    var Kce = $( "#Kce" ).val();

    if(!/^[0-9]+$/.test(Kce))
    {
        updateMsg( { status : false,
                     msg : "Kce must be an integer" } );
        return false;
    }

    Kce = parseInt(Kce);

    var Kem = $( "#Kem" ).val();

    if(!/^[0-9]+$/.test(Kem))
    {
        updateMsg( { status : false,
                     msg : "Kem must be an integer" } );
        return false;
    }

    Kem = parseInt(Kem);

    var Klik = $( "#Klik" ).val();

    if(!/^[0-9]+$/.test(Klik))
    {
        updateMsg( { status : false,
                     msg : "Klik must be an integer" } );
        return false;
    }

    Klik = parseInt(Klik);

    var Kcov = $( "#Kcov" ).val();

    if(!/^[0-9]+$/.test(Kcov))
    {
        updateMsg( { status : false,
                     msg : "Kcov must be an integer" } );
        return false;
    }

    Kcov = parseInt(Kcov);

    var rho = $( "#rho" ).val();
    rho = parseFloat(rho);
    
    var perturb = $( "#perturb" ).val();
    perturb = parseFloat(perturb);
    
    var alpha = $( "#alpha" ).val();
    alpha = parseFloat(alpha);
    
    var beta = $( "#beta" ).val();
    beta = parseFloat(beta);

    var gamma = $( "#gamma" ).val();
    gamma = parseFloat(gamma);

    var k = $( "#k" ).val();

    if(!/^[0-9]+$/.test(k))
    {
        updateMsg( { status : false,
                     msg : "k must be an integer" } );
        return false;
    }

    k = parseInt(k);

    var pcutoff = $( "#pcutoff" ).val();
    pcutoff = parseFloat(pcutoff);

    var qcutoff = $( "#qcutoff" ).val();
    qcutoff = parseFloat(qcutoff);

    var numIter = $( "#numIter" ).val();

    if(!/^[0-9]+$/.test(numIter))
    {
        updateMsg( { status : false,
                     msg : "numIter must be an integer" } );
        return false;
    }

    numIter = parseInt(numIter);

    var numConverge = $( "#numConverge" ).val();

    if(!/^[0-9]+$/.test(numConverge))
    {
        updateMsg( { status : false,
                     msg : "numConverge must be an integer" } );
        return false;
    }

    numConverge = parseInt(numConverge);

    return { jobName : jobName,
             crossEntropyStep : crossEntropyStep,
             emStep : emStep,
             uncertaintyStep : uncertaintyStep,
             seed : seed,
             Kce : Kce,
             Kem : Kem,
             Klik : Klik,
             Kcov : Kcov,
             rho : rho,
             perturb : perturb,
             apha : alpha,
             beta : beta,
             gamma : gamma,
             k : k,
             pcutoff : pcutoff,
             qcutoff : qcutoff,
             numIter : numIter,
             numConverge : numConverge};
}

var updateMsg = function(data)
{
    $( "#msg" ).text(data.msg);
    if(data.status)
        $( "#msg" ).prop('class', 'alert alert-success');
    else
        $( "#msg" ).prop('class', 'alert alert-error');
    $( "#msg" ).show();
};

var StochOptim = StochOptim || {}
var Import = Import || {}

Import.ArchiveSelect = Backbone.View.extend(
    {
        initialize: function(options)
        {
            this.$el = $( "#archiveSelect" );

            /*this.$el.change( function(event) {
                $( event.target ).find( "option:selected" ).trigger('select');
            });*/


            this.state = { selected : 0 };
            
            this.$el.hide();
        },

        attach: function(data)
        {
            this.data = data;

            this.state = { selected : 0 };

            this.render();

            this.trigger('select', data[0]);
        },

        render: function()
        {
            this.$el.empty();

            if(_.has(this, 'data')) {
                if(this.data.length > 0)
                {
                    $( "#archiveSelectDiv" ).show();
                }

                for(var i = 0; i < this.data.length; i++)
                {
                    var newOption = $( this.optionTemp( this.data[i]) ).appendTo( this.$el );

                    newOption.find('input').on('click', _.partial( function(data, view) {
                        view.trigger('select', data);
                    }, this.data[i], this));

                    newOption.find('a').click( _.partial(function(id, event) {
                        event.preventDefault();

                        $.post("/import?reqType=delJob&id=" + id,
                               success = function(data)
                               {
                                   location.reload();
                               });
                    }, this.data[i].id));
                }
            }

            this.$el.find('input').eq(0).click();

            this.$el.show();

            return this;
        }
    });

StochOptim.Controller = Backbone.View.extend(
    {
        el : $("#stochoptim"),

        // These are the states of the controller
        MODELSELECT : 1,
        SIMULATIONCONFIGURE : 2,
        RESULTSVIEW : 3,

        initialize : function(attributes)
        {
            // Set up room for the model select stuff
            // Pull in all the models from the internets
            // Build the simulationConf page (don't need external info to make that happen)
            this.attributes = attributes;

            this.stage = this.MODELSELECT;

            this.nextButton = undefined;

            // We gotta go off to the server and get this information
            this.models = undefined;

            // We gotta go off to the server and fetch this too
            this.model = undefined;

            // We gotta fetch this as well!
            this.csvFiles = undefined;

            this.on('select', _.bind(this.select, this) );

            // Draw a screen so folks have something to see
            this.render();

            // Go off and fetch those models and queue up a render on completion
            this.models = new stochkit.ModelCollection();

            // Go get the csvFiles we have hosted
            this.csvFiles = new fileserver.FileList( [], { key : 'stochoptimdata' } );

            // When finished, queue up another render
            this.models.fetch( { success : _.bind(this.render, this) } );

            this.csvFiles.fetch( { success : _.bind(this.render, this) } );
        },
        
        // This event gets fired when the user selects a csv data file
        select : function(data)
        {
            var preview = $( '#csvSeeDiv' ).find( '#preview' );

            preview.html( data.attributes.preview );
        },

        buttonClicked : function()
        {
            if(this.stage == this.MODELSELECT)
            {
                var id = parseInt($( "input:radio[name=model_to_simulate]:checked" ).val());

                this.model = this.models.get(id);
                this.stage = this.SIMULATIONCONFIGURE;
                this.render();
            }
            else if(this.stage == this.SIMULATIONCONFIGURE)
            {
            }
            else
            {
            }
        },

        render : function()
        {
            //If we're at the model select stage, just render the available models if that info has been fetched
            if(this.stage == this.MODELSELECT)
            {
                $( this.el ).empty();

                var modelSelectTemplate = _.template( $( "#modelSelectTemplate" ).html() );

                var data = undefined;

                if(typeof this.models != 'undefined')
                {
                    data = this.models.models;
                } 

                $( this.el ).html( modelSelectTemplate( { models : data } ) );

                // Set event handler on the next button

                this.nextButton = $( this.el ).find( "#next" )
                this.nextButton.click( _.bind( this.buttonClicked, this) );
            }
            //If the user clicks next, then we take the model and ask the user how they want it StochOptim'ed
            else if(this.stage == this.SIMULATIONCONFIGURE)
            {
                $( this.el ).empty();

                var simulationConfTemplate = _.template( $( "#simulationConfTemplate" ).html() );

                $( this.el ).html( simulationConfTemplate( { model : this.model, csvFiles : this.csvFiles } ) );

                if(typeof this.csvFiles != 'undefined')
                {
                    var csvSelect = $( this.el ).find('#csvSelect');

                    for(var i = 0; i < this.csvFiles.models.length; i++)
                    {

	                this.optionTemp = _.template('<tr> \
<td><a href="javascript:preventDefault();">Delete</a></td><td><input type="radio" name="archive"></td><td><%= attributes.name %></td>\
</tr>');

                        var newOption = $( this.optionTemp( this.csvFiles.models[i]) ).appendTo( csvSelect );

                        // When the csvFiles gets selected, an event files on this object! (with the appropriate csvFile as the ag)
                        newOption.find('input').on('click', _.partial( function(data, view) {
                            view.trigger('select', data);
                        }, this.csvFiles.models[i], this));

                        // When the delete button gets clicked, a delete msg is sent
                        newOption.find('a').click( _.partial(function(data, event) {
                            data.destroy(); // After the file is deleted, we should post up a msg
                            event.preventDefault();
                        }, this.csvFiles.models[i]));
                    }

                    $( this.el ).find('#fileupload').fileupload({
                        url: '/FileServer/large/' + 'stochoptimdata',
                        dataType: 'json',
                        send: function (e, data) {
                            names = "";
                            
                            for(var i in data.files)
                            {
                                names += data.files[i].name + " ";
                            }
                            
                            var progressbar = _.template('<span><%= name %> :<div class="progress"> \
<div class="bar" style="width:0%;"> \
</div> \
</div> \
</span>');

                            progressHandle = $( progressbar({ name : names }) ).appendTo( "#progresses" );
                        },
                        done: function (e, data) {
                            progressHandle.remove();
                        },
                        progressall: function (e, data) {
                            var progress = parseInt(data.loaded / data.total * 100, 10);
                            progressHandle.find('.bar' ).css('width', progress + '%');
                            progressHandle.find('.bar' ).text(progress + '%');
                        },
                        error : function(data) {
                            updateMsg( { status : false,
                                         msg : "Server error uploading file" } );
                        }
                    }).prop('disabled', !$.support.fileInput)
                        .parent().addClass($.support.fileInput ? undefined : 'disabled');

                    // Have something selected
                    csvSelect.find('input').eq(0).click();
                }
            }
            else if(this.stage == this.RESULTSVIEW)
            {
            }
        }
    }
);

var run = function()
{
    //var id = $.url().param("id");

    var cont = new StochOptim.Controller();
}
