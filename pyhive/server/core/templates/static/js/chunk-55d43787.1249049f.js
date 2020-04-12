(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-55d43787"],{"4a11":function(t,e,n){"use strict";n.r(e);var s=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",{staticClass:"panel"},[n("panel-title",{attrs:{title:t.$lang.objects.clients}},[n("el-button",{attrs:{size:"mini"},on:{click:t.onRefresh}},[n("i",{staticClass:"fa fa-refresh"}),t._v("\n\t\t\t"+t._s(t.$lang.buttons.refresh)+"\n\t\t")]),n("router-link",{attrs:{to:{name:"clientCreate"},tag:"span"}},[n("el-button",{attrs:{type:"success",size:"mini"}},[n("i",{staticClass:"fa fa-plus"}),t._v("\n\t\t\t\t"+t._s(t.$lang.buttons.create)+"\n\t\t\t")])],1)],1),n("div",{staticClass:"panel-body"},[n("el-table",{directives:[{name:"loading",rawName:"v-loading",value:t.loading,expression:"loading"}],attrs:{"empty-text":t.$lang.messages.noData,data:t.clients,"element-loading-text":t.$lang.messages.loading}},[n("el-table-column",{attrs:{align:"center",label:t.$lang.columns.status,width:"120"},scopedSlots:t._u([{key:"default",fn:function(e){return[1===t.clientsStatus[e.row.pk]?n("el-button",{attrs:{type:"success",size:"mini"}},[t._v(t._s(t.$lang.buttons.normal))]):0===t.clientsStatus[e.row.pk]?n("el-button",{attrs:{type:"warning",size:"mini"}},[t._v(t._s(t.$lang.buttons.connecting))]):n("el-button",{attrs:{type:"danger",size:"mini"}},[t._v(t._s(t.$lang.buttons.error))])]}}])}),n("el-table-column",{attrs:{align:"center",prop:"pk",label:t.$lang.columns.id,width:"80"}}),n("el-table-column",{attrs:{align:"center",prop:"fields.name",label:t.$lang.columns.name,width:"160"}}),n("el-table-column",{attrs:{align:"center",prop:"fields.ip",label:t.$lang.columns.ip,width:"200"}}),n("el-table-column",{attrs:{align:"center",prop:"fields.port",label:t.$lang.columns.port,width:"120"}}),n("el-table-column",{attrs:{align:"center",prop:"fields.auth",width:"150",label:t.$lang.columns.auth},scopedSlots:t._u([{key:"default",fn:function(t){return[t.row.fields.auth?n("i",{staticClass:"fa fa-check-circle",staticStyle:{"font-size":"20px",color:"#67C23A"}}):n("i",{staticClass:"fa fa-times-circle",staticStyle:{"font-size":"20px",color:"#F56C6C"}})]}}])}),n("el-table-column",{attrs:{align:"center",prop:"fields.spider_amount",width:"120",label:t.$lang.columns.spiderAmount}}),n("el-table-column",{attrs:{align:"center",label:t.$lang.columns.operations},scopedSlots:t._u([{key:"default",fn:function(e){return[n("router-link",{attrs:{to:{name:"clientEdit",params:{id:e.row.pk}},tag:"span"}},[n("el-button",{attrs:{type:"warning",size:"mini"}},[n("i",{staticClass:"fa fa-edit"}),t._v("\n\t\t\t\t\t\t\t"+t._s(t.$lang.buttons.edit)+"\n\t\t\t\t\t\t")])],1),n("el-button",{attrs:{type:"primary",size:"mini",disabled:!(1===t.clientsStatus[e.row.pk])},on:{click:function(n){return t.goClientSchedule(e.row.pk)}}},[n("i",{staticClass:"fa fa-sitemap"}),t._v("\n\t\t\t\t\t\t"+t._s(t.$lang.buttons.schedule)+"\n\t\t\t\t\t")]),n("el-button",{attrs:{type:"danger",size:"mini"},on:{click:function(n){return t.onSingleDelete(e.row.pk)}}},[n("i",{staticClass:"fa fa-remove"}),t._v("\n\t\t\t\t\t\t"+t._s(t.$lang.buttons.delete)+"\n\t\t\t\t\t")])]}}])})],1)],1)],1)},a=[],l=(n("ac6a"),n("eee4")),i={name:"ClientIndex",props:{},data:function(){return{clients:null,loading:!0,clientsStatus:{}}},components:{PanelTitle:l["a"]},created:function(){this.onGetClientData()},methods:{onRefresh:function(){this.onGetClientData()},onGetClientsStatus:function(){var t=this;this.clients.forEach(function(e){t.onGetClientStatus(e.pk)})},onGetClientStatus:function(t){var e=this;this.$set(this.clientsStatus,t,0),this.$http.get(this.formatString(this.$store.state.url.client.status,{id:t})).then(function(n){var s=n.data.result;e.$set(e.clientsStatus,t,parseInt(s))}).catch(function(){e.$set(e.clientsStatus,t,-1)})},onGetClientData:function(){var t=this;this.loading=!0,this.$http.get(this.$store.state.url.client.index).then(function(e){var n=e.data;t.clients=n,t.loading=!1,t.onGetClientsStatus()}).catch(function(){t.loading=!1})},onDeleteClient:function(t){var e=this;this.$http.post(this.formatString(this.$store.state.url.client.remove,{id:t})).then(function(){e.$message.success(e.$store.getters.$lang.messages.successDelete),e.loading=!1,e.onGetClientData()}).catch(function(){e.$message.error(e.$store.getters.$lang.messages.errorDelete),e.loading=!1})},onSingleDelete:function(t){var e=this;this.$confirm(this.$store.getters.$lang.messages.confirm,this.$store.getters.$lang.buttons.confirm,{confirmButtonText:this.$store.getters.$lang.buttons.yes,cancelButtonText:this.$store.getters.$lang.buttons.no,type:"warning"}).then(function(){e.onDeleteClient(t)})},goClientSchedule:function(t){this.$router.push({name:"clientSchedule",params:{id:t}})}}},o=i,r=n("2877"),c=Object(r["a"])(o,s,a,!1,null,null,null);e["default"]=c.exports},eee4:function(t,e,n){"use strict";var s=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",{staticClass:"panel-title"},[t.title?n("span",{domProps:{textContent:t._s(t.title)}}):t._e(),n("div",{staticClass:"fr"},[t._t("default")],2)])},a=[],l={name:"PanelTitle",props:{title:{type:String}}},i=l,o=n("2877"),r=Object(o["a"])(i,s,a,!1,null,null,null);e["a"]=r.exports}}]);
//# sourceMappingURL=chunk-55d43787.1249049f.js.map