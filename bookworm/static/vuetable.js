//Vue dynamic grid with editing capabilities
Vue.component('vuegrid', {
    template: '#vuegrid-template',
    props:{
	columns: Array,
	table_data: Array,
	options: Object,
	sortOrder: Object,
    },
    data: function(){
	var pages = [];
	var currentPage = 0;
	var pageSizes = [10,20,40,60,80,100];
	var spanLength = this.columns.length - 1;

	return {
	    currentPage: currentPage,
	    pageSize: pageSizes[0],  //set default page
	    pageSizes: pageSizes,
	    pages: pages,
	    filterKey: "",
	    editTable: false,
	    headerSpan_Length: spanLength,
	};
    },
    filters:{
	handleCheckBox: function(row, col){
	    if(col.type == 'checkbox'){
		if(row[col.name] === undefined || row[col.name] == false){
		    return 'No';
		}
		return 'Yes';
	    }
	    return row[col.name];
	}
    },
    methods: {
	deleteSelected: function(){
	    var filteredRecords = this.filteredRecords;
	    var deletedRecords = [];

	    filteredRecords.forEach(row => {
		if(row.select_flag){
		    deletedRecords.push(Object.assign({},row));
		}
	    });

	    this.$emit('delete_operation', deletedRecords);
	}
    },
    watch: {
	filterKey: function(){
	    this.currentPage = 0;
	},
	pageSize: function(){
	    this.currentPage = 0;
	},
    },
    computed:{
	filteredRecords: function(){
	    var records = this.table_data;
	    var filter = this.filterKey.toLowerCase();

	    //Apply filter
	    if(filter){
		records = records.filter(row => {
		    return Object.keys(row).some(key =>{
			return String(row[key]).toLowerCase().indexOf(filter) > -1;
		    })
		})
	    }

	    return records;
	},
	currentPageRecords: function(){
	    var records = this.filteredRecords;
	    var pageSizes = this.pageSizes;
	    var pageSize = this.pageSize;
	    var pages = this.pages;
	    var page = this.currentPage;

	    //Pagination
	    //Determine pages based on pageSize and records.length
	    this.pages = [];
	    for(x=0;x<(Math.ceil(records.length/pageSize));x++){
		this.pages.push(x);
	    }

	    //slice current page
	    records = records.slice(page*pageSize, ((page+1)*pageSize));

	    //add relative index for display purposes
	    let start_index = page*pageSize;
	    records = records.map(function(elem){
		elem['index'] = start_index;
		start_index++;

		return elem;
	    });

	    return JSON.parse(JSON.stringify(records));
	},
	selectAll: {
	    get: function(){
		var records = this.filteredRecords;
		return records.every(elem =>{
		    return elem.select_flag;
		});
	    },
	    set: function(newValue){
		var records = this.filteredRecords;
		records.forEach(elem=> {
		    //if select flag is not set, set it.
		    if(elem.select_flag != newValue){
			var Obj = Object.assign({}, elem);
			Obj.select_flag = newValue;
			this.$emit('update_row', Obj, 'select_flag', newValue)
		    }
		});
	    }
	},
	pageFrom: function(){
	    //handle no records
	    if(this.filteredRecords.length == 0 )
		return 0;
	    return (this.currentPage * this.pageSize)+1;
	},
	pageTo: function(){
	    //handle records count on last page
	    var to = (this.currentPage + 1) * this.pageSize;
	    var lastRecord = this.filteredRecords.length;

	    return (to >= lastRecord ? lastRecord : to);
	},
	deleteBtn: function(){
	    var records = this.filteredRecords;
	    return records.some(elem => {
		return elem.select_flag;
	    });
	}
    }
});

//Vue table app
function vuetable(rows, cols, options){
    return new Vue({
	data: {
	    table_records: rows,
	    columns: cols,
	    table_options: options,
	    dependents: [],
	    modified_records: new Set(),
	    deleted_records: [],
	    sortOrder: {},
	    sortKey: "",
	    unique_id: 0,
	},
	created: function() {
	    var dates = [];
	    var records = this.table_records;
	    var columns = this.columns;
	    var sortOrder = this.sortOrder;
	    var tmp_obj = {};
	    var unique_id = this.unique_id;
	    var dependents = this.dependents;

	    //Set default sorting order
	    columns.forEach(elem => {
		tmp_obj[elem.name] = 0;
	    });

	    Object.assign(sortOrder,tmp_obj);

	    //Parse and format date types
	    dates = this.columns.filter(function(elem){
		return elem.type == 'date';
	    });
	    rows.map(function(row){
		dates.forEach(function(elem){
		    row[elem.name] = (new Date(Date.parse(row[elem.name]))).toLocaleString('fr-CA', { year: "numeric", month: "2-digit",day: "2-digit" });

		})
		return row;
	    });

	    //Add unique_id, selection flag for internal purpose
	    columns.splice(0,0,{name: 'select_flag', type: 'checkbox', header: 'Select', modifiable: true, internal_use: true, sortable: false});
	    records = records.map(function(elem,index){

		if(!(elem.hasOwnProperty('unique_id'))){
		    Object.assign(elem, {unique_id: unique_id});
		    unique_id++;
		}
		if(!(elem.hasOwnProperty('select_flag'))){
		    Object.assign(elem, {select_flag: false});
		}
	    })
	    this.unique_id = unique_id;

	    //Identify dependent columns
	    columns.forEach(col => {
		if(col.dependents){
		    dependents.push(col.dependents.func);
		}
	    });
	},
	watch: {
	    table_records: function(oldValue, newValue){
		var records = this.table_records;
		var unique_id = this.unique_id;
		var modifiedRecords = this.modified_records;
		
		if(records.length == 0){
		    modifiedRecords.clear();
		    unique_id = 0;
		}
		
		//add unique_id, selecion and deletion flag
		records.forEach(elem => {
		    if(!(elem.hasOwnProperty('select_flag'))){
			Object.assign(elem,{select_flag: false});
		    }
		    if(!elem.hasOwnProperty('unique_id')){
			Object.assign(elem,{unique_id: unique_id});
			unique_id++;
		    }
		});

		//update unique_id with the last id used
		this.unique_id = unique_id;
	    }
	},
	methods: {
	    /* Methods for internal use */
	    sortBy: function(col){
		var sortOrder = this.sortOrder;
		var sortKey = this.sortKey;
		var records = this.table_records;

		sortKey = col.name;
		(sortOrder[sortKey] === 0) ? sortOrder[sortKey] = 1 : sortOrder[sortKey] *= -1;

		//Apply sort
		if(sortKey.length){
		    records.sort(function(first, second){
			var a = first[sortKey];
			var b = second[sortKey];

			if(typeof a === "number" || typeof b === "number"){
			    a = a.toString();
			    b = b.toString();
			}
			
			//Handle null and empty strings
			if(a == null || b == null){
			    return (a == null && b == null) ? 0 : (a == null && b != null) ? 1: -1;
			}
			if(a == "" || b == ""){
			    return (a == "" && b == "") ? 0 : (a == "" && b != "") ? 1: -1;
			}


			return (a.localeCompare(b, undefined,{numeric: true, sensitivity: 'base'}) * sortOrder[sortKey]);			
		    });
		}
	    },
	    deleteOperation: function(deletedRecords){
		var records = this.table_records;
		var modifiedRecords = this.modified_records;
		var removedRecords = this.deleted_records;
		var ids = [];

		removedRecords.splice(removedRecords.length, 0, ...deletedRecords);
		
		deletedRecords.forEach(elem => {
		    var index = records.findIndex(row => {
			return row.unique_id == elem.unique_id;
		    });

		    records.splice(index, 1);
		});
		
		//Update modification tracker
		ids.forEach(elem => {
		    modifiedRecords.delete(elem);
		});
	    },
	    addRow: function(){
		var obj = {};
		var columns = this.columns;

		columns.forEach(elem => {
		    obj[elem.name] = null;
		});
		
		this.table_records.splice(this.table_records.length,1, obj);
	    },
	    updateRow: function(row){
		var id = row['unique_id'];
		var records = this.table_records;
		var modifiedRecords = this.modified_records;
		var index = null;
		var internalColumns = [];
		var columns = this.columns;
		var old_record = null;
		var dependencies = this.dependents;

		//Run dependency function based on new values
		dependencies.forEach(func => {
		    func(row);
		});

		//Get index of old row
		index = records.findIndex(elem => {
		    return id == elem.unique_id;
		});

		old_record = records[index];

		//Update table
		records.splice(index,1,row);
		

		//Keep track of modified records
		//Ignore columns that are used for internal use
		internalColumns = columns.filter(elem=>{
		    return elem.internal_use === undefined ? false : true;
		});

		for(let key of Object.keys(row)){
		    if(old_record[key] !== row[key] && (!(internalColumns.some(elem =>{return elem.name == key;})))){
			    modifiedRecords.add(id);
			    break;
		    }
		}
	    },

	    /* Methods for external use */
	    getNewRecords: function(){
		return this.table_records;
	    },
	    getModifiedRecords: function(){
		var modifiedIds = this.modified_records;
		var records = this.table_records;
		var modifiedRecords = [];

		modifiedRecords = records.filter(elem=>{
		    return modifiedIds.has(elem.unique_id);
		});

		return modifiedRecords;
	    },
	    getDeletedRecords: function(){
		return this.deleted_records;
	    },
	    resetModificationTracker: function(){
	    },
	    resetDeletionTracker: function(){
		this.deleted_records.splice(0, this.deleted_records.length);
	    },

	},
    })
}

//Return message handling
var msg = new Vue({
    el: '#msg_box',
    data: {
	messages: [],
	old_messages: [],
    },
    methods: {
	add_messages: function(msgs){
	    old_msgs = this.old_messages;
	    displayed_msgs = this.messages;

	    // Archive displayed messages
	    old_msgs.splice(old_msgs.length,0, ...displayed_msgs);

	    //Update displayed messages
	    displayed_msgs.splice(0, displayed_msgs.length, ...msgs);
	}
    }
})

