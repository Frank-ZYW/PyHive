<template>
	<div class="panel">
		<panel-title :title="$lang.objects.clients">
			<el-button @click="onRefresh" size="mini">
				<i class="fa fa-refresh"></i>
				{{ $lang.buttons.refresh }}
			</el-button>
			<router-link :to="{name: 'clientCreate'}" tag="span">
				<el-button type="success" size="mini">
					<i class="fa fa-plus"></i>
					{{ $lang.buttons.create }}
				</el-button>
			</router-link>
		</panel-title>
		<div class="panel-body">
			<el-table :empty-text="$lang.messages.noData" :data="clients" v-loading="loading" :element-loading-text="$lang.messages.loading">
				<el-table-column align="center" :label="$lang.columns.status" width="120">
					<template slot-scope="props">
						<el-button v-if="clientsStatus[props.row.pk] === 1" type="success" size="mini">{{ $lang.buttons.normal }}</el-button>
						<el-button v-else-if="clientsStatus[props.row.pk] === 0" type="warning" size="mini">{{ $lang.buttons.connecting }}</el-button>
						<el-button v-else type="danger" size="mini">{{ $lang.buttons.error }}</el-button>
					</template>
				</el-table-column>
				<el-table-column align="center" prop="pk" :label="$lang.columns.id" width="80"/>
				<el-table-column align="center" prop="fields.name" :label="$lang.columns.name" width="160"/>
				<el-table-column align="center" prop="fields.ip" :label="$lang.columns.ip" width="200"/>
				<el-table-column align="center" prop="fields.port" :label="$lang.columns.port" width="120"/>
				<el-table-column align="center" prop="fields.auth" width="150" :label="$lang.columns.auth">
					<template slot-scope="props">
						<i v-if="props.row.fields.auth" class="fa fa-check-circle" style="font-size:20px; color:#67C23A"/>
						<i v-else class="fa fa-times-circle" style="font-size:20px; color:#F56C6C"/>
					</template>
				</el-table-column>
				<el-table-column align="center" prop="fields.spider_amount" width="120" :label="$lang.columns.spiderAmount"/>
				<el-table-column align="center" :label="$lang.columns.operations">
					<template slot-scope="props">
						<router-link :to="{name: 'clientEdit', params: {id: props.row.pk}}" tag="span">
							<el-button type="warning" size="mini">
								<i class="fa fa-edit"></i>
								{{ $lang.buttons.edit }}
							</el-button>
						</router-link>
						<el-button type="primary" size="mini" :disabled="!(clientsStatus[props.row.pk] === 1)" @click="goClientSchedule(props.row.pk)">
							<i class="fa fa-sitemap"></i>
							{{ $lang.buttons.schedule }}
						</el-button>
						<el-button type="danger" size="mini" @click="onSingleDelete(props.row.pk)">
							<i class="fa fa-remove"></i>
							{{ $lang.buttons.delete }}
						</el-button>
					</template>
				</el-table-column>
			</el-table>
		</div>
	</div>
</template>

<script>
	import PanelTitle from '../../components/PanelTitle'

	export default {
		name: 'ClientIndex',
		props: {},
		data() {
			return {
				clients: null,
				loading: true,
				// to store batch selected id of client
				clientsStatus: {}
			}
		},
		components: {
			PanelTitle,
		},
		created() {
			this.onGetClientData()
		},
		methods: {
			onRefresh() {
				this.onGetClientData()
			},
			onGetClientsStatus() {
				this.clients.forEach((client) => {
					this.onGetClientStatus(client.pk)
				})
			},
			onGetClientStatus(id) {
				this.$set(this.clientsStatus, id, 0);
				this.$http.get(this.formatString(this.$store.state.url.client.status, {
					id: id
				})).then(({data: {result: result}}) => {
					this.$set(this.clientsStatus, id, parseInt(result));
				}).catch(() => {
					this.$set(this.clientsStatus, id, -1)
				})
			},
			onGetClientData() {
				this.loading = true;
				this.$http.get(this.$store.state.url.client.index
				).then(({data: clients}) => {
					this.clients = clients;
					this.loading = false;
					this.onGetClientsStatus()
				}).catch(() => {
					this.loading = false
				})
			},
			onDeleteClient(id) {
				this.$http.get(this.formatString(this.$store.state.url.client.remove, {
					id: id
				})).then(() => {
					this.$message.success(this.$store.getters.$lang.messages.successDelete);
					this.loading = false;
					this.onGetClientData();
				}).catch(() => {
					this.$message.error(this.$store.getters.$lang.messages.errorDelete);
					this.loading = false;
				})
			},
			onSingleDelete(id) {
				this.$confirm(this.$store.getters.$lang.messages.confirm, this.$store.getters.$lang.buttons.confirm, {
					confirmButtonText: this.$store.getters.$lang.buttons.yes,
					cancelButtonText: this.$store.getters.$lang.buttons.no,
					type: 'warning'
				}).then(() => {
					this.onDeleteClient(id)
				})
			},
			goClientSchedule(id){
				this.$router.push({name: 'clientSchedule', params: {id: id}})
			}
		}
	}
</script>