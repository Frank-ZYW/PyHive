<template>
	<div class="panel" id="project-index">
		<el-dialog :visible.sync="createProjectDialog" size="tiny" width="400px" class="dialog">
			<el-tabs v-model="activeDialogTab">
				<el-tab-pane :label="$lang.columns.upload" name="upload">
					<el-upload class="upload" drag accept=".zip" :action="$store.state.url.project.upload">
						<i class="el-icon-upload"></i>
						<div class="el-upload__text">{{ $lang.messages.dragOrSelect }}</div>
						<div class="el-upload__tip" slot="tip">{{ $lang.messages.supportZip }}</div>
					</el-upload>
				</el-tab-pane>
			</el-tabs>
			<div slot="footer">
				<el-button @click="createProjectDialog=false" size="small">
					{{ $lang.buttons.cancel }}
				</el-button>
				<el-button @click="onUploadedProject()" v-if="activeDialogTab === 'upload'" type="primary" size="small">
					{{ $lang.buttons.finish }}
				</el-button>
			</div>
		</el-dialog>
		<el-dialog :visible.sync="deployProjectDialog" size="tiny" width="1050px" class="dialog">
			<div class="panel">
				<panel-title :title="$lang.objects.clients"/>
				<div class="panel-body">
					<el-alert :title="$lang.messages.deployNotice" type="warning"/>
					<el-table
							ref="deployTable"
							:empty-text="$lang.messages.noData"
							:data="clients"
							v-loading="dialogLoading"
							:element-loading-text="$lang.messages.loading"
							:header-cell-class-name="headCellClass"
							@row-click="handleSelectionChange">
						<el-table-column align="center" type="selection" :selectable="checkSelectable" width="55" />
						<el-table-column align="center" :label="$lang.columns.status" width="120">
							<template slot-scope="props">
								<el-button v-if="clientsStatus[props.row.pk] === 1" type="success" size="mini">{{ $lang.buttons.normal }}</el-button>
								<el-button v-else-if="clientsStatus[props.row.pk] === 0" type="warning" size="mini">{{ $lang.buttons.connecting }}</el-button>
								<el-button v-else type="danger" size="mini">{{ $lang.buttons.error }}</el-button>
							</template>
						</el-table-column>
						<el-table-column align="center" prop="pk" :label="$lang.columns.id" width="80"/>
						<el-table-column align="center" prop="fields.name" :label="$lang.columns.name" width="200"/>
						<el-table-column align="center" prop="fields.ip" :label="$lang.columns.ip" width="160"/>
						<el-table-column align="center" prop="fields.port" :label="$lang.columns.port" width="150"/>
						<el-table-column align="center" prop="fields.spider_amount" width="130" :label="$lang.columns.spiderAmount"/>
					</el-table>
				</div>
			</div>
			<div slot="footer">
				<el-button @click="deployProjectDialog=false" size="small">
					{{ $lang.buttons.cancel }}
				</el-button>
				<el-button @click="onProjectDeploy()" :disabled="!ifChecked" type="primary" size="small">
					{{ $lang.buttons.deploy }}
				</el-button>
			</div>
		</el-dialog>

		<panel-title :title="$lang.objects.project">
			<el-input v-model="keyword" :placeholder="$lang.inputs.search" prefix-icon="el-icon-search" size="mini" @input="getProjectData" style="width:160px; margin-right:10px"/>
			<el-button @click.stop="onRefresh" size="mini">
				<i class="fa fa-refresh"></i>
				{{ $lang.buttons.refresh }}
			</el-button>
			<el-button type="primary" size="mini" @click="createProjectDialog=true">
				<i class="fa fa-plus"></i>
				{{ $lang.buttons.createOrUpdate }}
			</el-button>
		</panel-title>
		<div class="panel-body">
			<el-table :data="projects" :empty-text="$lang.messages.noData" v-loading="loading" :element-loading-text="$lang.messages.loading" :style="{width: '100%'}" max-height="700">
				<el-table-column align="center" prop="name" :label="$lang.columns.name" width="150"/>
                <el-table-column align="center" :label="$lang.columns.deployedVersion" width="350">
					<template slot-scope="scope">
						<span v-if="scope.row.client">
							<el-tag type="info" size="medium">{{scope.row.deployed_version}}</el-tag>
							<span style="margin-left:10px;">
								<i class="fa fa-bug"></i>
								{{$lang.tags.spiderAmount}}
								<el-badge class="mark" :value="scope.row.spider_amount"/>
							</span>
							<el-divider direction="vertical"></el-divider>
							<span style="color:#909399">
								<i class="fa fa-clock-o" style="margin-right:3px"></i>
								{{scope.row.deployed_at}}
							</span>
						</span>
						<span v-else>{{ $lang.messages.nullValue }}</span>
					</template>
				</el-table-column>
				<el-table-column align="center" :label="$lang.columns.latestVersion" width="350">
					<template slot-scope="scope">
						<el-tag size="medium">{{scope.row.uploaded_version}}</el-tag>
						<span>
							<el-tooltip v-if="scope.row.if_built" :content="scope.row.egg" placement="top">
								<el-tag  size="medium">{{ $lang.tags.built }}</el-tag>
							</el-tooltip>
							<el-tag v-else type="danger" size="medium">{{ $lang.tags.unBuild }}</el-tag>
						</span>
						<el-divider direction="vertical"></el-divider>
						<span style="color:#909399">
							<i class="fa fa-clock-o" style="margin-right:3px"></i>
							{{scope.row.updated_at}}
						</span>
					</template>
				</el-table-column>
				<el-table-column align="center" :label="$lang.columns.client" width="250">
					<template slot-scope="scope">
						<i class="el-icon-s-home" style="margin-right:3px"></i>
						<span v-if="scope.row.client">{{ scope.row.client_name }}</span>
						<span v-else>{{ $lang.messages.nullValue }}</span>
					</template>
				</el-table-column>
				<el-table-column align="center" :label="$lang.columns.operations">
					<template slot-scope="props">
						<router-link :to="{name: 'projectEdit', params: {name: props.row.name}}" tag="span">
							<el-button type="warning" size="mini">
								<i class="fa fa-edit"></i>
								{{ $lang.buttons.code }}
							</el-button>
						</router-link>
						<el-dropdown trigger="click" size="medium">
							<el-button type="primary" size="mini">
								<i class="fa fa-cloud"></i>
								{{ $lang.buttons.deployAction }}
								<i class="el-icon-arrow-down"></i>
							</el-button>
							<el-dropdown-menu slot="dropdown">
								<el-dropdown-item :disabled="!props.row.if_built" @click.native="goProjectDeploy(props.row)">
									<i class="fa fa-cloud-upload"></i>
									{{ $lang.buttons.deploy }}
								</el-dropdown-item>
								<el-dropdown-item :disabled="!props.row.client" @click.native="onSingleWithdraw(props.row.name)">
									<i class="fa fa-undo"></i>
									{{ $lang.buttons.withdraw }}
								</el-dropdown-item>
								<el-dropdown-item @click.native="onProjectBuild(props.row.name)">
									<i class="fa fa-codepen"></i>
									{{ $lang.buttons.build }}
								</el-dropdown-item>
							</el-dropdown-menu>
						</el-dropdown>
						<el-button type="danger" size="mini" @click="onSingleDelete(props.row)">
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
		name: 'ProjectIndex',
		data() {
			return {
				keyword: '',
				activeDialogTab: 'upload',
				createProjectDialog: false,
				deployProjectDialog: false,
				gitAddress: null,
				projects: [],
				loading: false,
				dialogLoading: false,
				clients: null,
				clientsStatus: {},
				deployInfo: {},
				ifChecked: null
			}
		},
		components: {
			PanelTitle,
		},
		created() {
			this.getProjectData()
		},
		methods: {
			getProjectData() {
				this.loading = true;
				this.$http.get(this.formatString(this.$store.state.url.project.index, {
					keyword: this.keyword
				})).then(({data: projects}) => {
					this.projects = projects;
					this.loading = false;
				}).catch(() => {
					this.loading = false
				})
			},
			onRefresh() {
				this.getProjectData()
			},
			onDeleteProject(name) {
				this.loading = true;
				this.$http.get(this.formatString(this.$store.state.url.project.remove, {
					name: name
				})).then(() => {
					this.onRefresh();
					this.$message.success(this.$store.getters.$lang.messages.successDelete)
				}).catch(() => {
					this.loading = false;
					this.$message.error(this.$store.getters.$lang.messages.errorDelete)
				})
			},
			onSingleDelete(row) {
				if(!row.client){
					this.$confirm(this.$store.getters.$lang.messages.confirm, this.$store.getters.$lang.buttons.confirm, {
						confirmButtonText: this.$store.getters.$lang.buttons.yes,
						cancelButtonText: this.$store.getters.$lang.buttons.no,
						type: 'warning'
					}).then(() => {
						this.onDeleteProject(row.name)
					})
				} else {
					this.$message.error(this.$store.getters.$lang.messages.withdrawFirst);
				}
			},
			onUploadedProject() {
				this.createProjectDialog = false;
				this.onRefresh()
			},
			onProjectWithdraw(name){
				this.loading = true;
				this.$http.get(this.formatString(this.$store.state.url.project.withdraw, {
					name: name
				})).then(() => {
					this.onRefresh();
					this.$message.success(this.$store.getters.$lang.messages.successWithdraw)
				}).catch(() => {
					this.loading = false;
					this.$message.error(this.$store.getters.$lang.messages.errorWithdraw)
				})
			},
			onSingleWithdraw(name) {
				this.$confirm(this.$store.getters.$lang.messages.confirm, this.$store.getters.$lang.buttons.confirm, {
					confirmButtonText: this.$store.getters.$lang.buttons.yes,
					cancelButtonText: this.$store.getters.$lang.buttons.no,
					type: 'warning'
				}).then(() => {
					this.onProjectWithdraw(name)
				})
			},
			onProjectBuild(name) {
				this.loading = true;
				this.$http.get(this.formatString(this.$store.state.url.project.build, {
					name: name
				})).then(() => {
					this.onRefresh();
					this.$message.success(this.$store.getters.$lang.messages.successBuild)
				}).catch(() => {
					this.loading = false;
					this.$message.error(this.$store.getters.$lang.messages.errorBuild)
				})
			},
			goProjectDeploy(row){
				if (row.client) {
					this.loading = true;
					this.$http.get(this.formatString(this.$store.state.url.client.projectDeploy, {
						id: row.client,
						name: row.name,
					})).then(() => {
						this.onRefresh();
						this.$message.success(this.$store.getters.$lang.messages.successDeploy)
					}).catch(() => {
						this.loading = false;
						this.$message.error(this.$store.getters.$lang.messages.errorDeploy)
					})
				} else {
					this.ifChecked = false;
					this.deployInfo.project = row.name;
					this.deployProjectDialog = true;
					this.onGetClientData()
				}
			},
			onProjectDeploy(){
				this.deployProjectDialog = false;
				this.loading = true;
				this.$http.get(this.formatString(this.$store.state.url.client.projectDeploy, {
					id: this.deployInfo.client,
					name: this.deployInfo.project,
				})).then(() => {
					this.onRefresh();
					this.$message.success(this.$store.getters.$lang.messages.successDeploy)
				}).catch(() => {
					this.loading = false;
					this.$message.error(this.$store.getters.$lang.messages.errorDeploy)
				})
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
				this.dialogLoading = true;
				this.$http.get(this.$store.state.url.client.index
				).then(({data: clients}) => {
					this.clients = clients;
					this.onGetClientsStatus();
					this.dialogLoading = false
				}).catch(() => {
					this.dialogLoading = false
				})
			},
			handleSelectionChange(row) {
				if (this.clientsStatus[row.pk] === 1) {
					this.$refs.deployTable.clearSelection();
					if (this.deployInfo.client === row.pk) {
						this.deployInfo.client = null;
						this.ifChecked = false
					} else {
						this.$refs.deployTable.toggleRowSelection(row);
						this.deployInfo.client = row.pk;
						this.ifChecked = true
					}
				} else {
					this.$message.warning(this.$store.getters.$lang.messages.selectUnavailable)
				}
			},
			checkSelectable(row) {
				return this.clientsStatus[row.pk] === 1
			},
			headCellClass(row){
				if (row.columnIndex === 0) {
					return 'disabledCheck'
				}
			}
		}
	}
</script>

<style lang="scss">
	#project-index {
		.dialog {
			.el-dialog__body {
				padding-bottom: 0;
				padding-left: 40px;
				padding-right: 40px;
			}
		}
		.upload {
			width: 100%;
			.el-upload {
				width: 100%;
				.el-upload-dragger {
					width: 100%;
				}
			}
		}
	}

	.el-tag{
		margin-left: 10px;
	}

	.el-table /deep/.disabledCheck .cell .el-checkbox__inner{
		display: none!important;
	}
</style>