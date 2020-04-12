<template>
	<div class="panel">
		<el-dialog :visible.sync="intervalsDialog" size="tiny" width="500px" class="dialog">
			<el-form label-width="140px">
				<el-form-item :label="$lang.columns.intervals">
					<el-input v-model="intervals" :placeholder="$lang.columns.days"></el-input>
				</el-form-item>
			</el-form>
			<div slot="footer">
				<el-button @click="intervalsDialog=false" size="small">
					{{ $lang.buttons.cancel }}
				</el-button>
				<el-button @click="onSpiderIntervalsUpdte" type="primary" size="small">
					{{ $lang.buttons.save }}
				</el-button>
			</div>
		</el-dialog>

		<panel-title :title="$lang.objects.spiders">
			<el-input v-model="keyword" :placeholder="$lang.inputs.search" prefix-icon="el-icon-search" size="mini" @input="onGetSpiderData" style="width:160px; margin-right:10px"/>
			<el-button @click="onRefresh" size="mini">
				<i class="fa fa-refresh"></i>
				{{ $lang.buttons.refresh }}
			</el-button>
		</panel-title>
		<div class="panel-body">
			<el-table :empty-text="$lang.messages.noData" :data="spiders" v-loading="loading" :element-loading-text="$lang.messages.loading" :row-class-name="tableRowClassName" max-height="700">
				<el-table-column align="center" prop="id" :label="$lang.columns.id" width="80"/>
				<el-table-column align="center" :label="$lang.columns.name" width="200">
					<template slot-scope="props">
						{{ props.row.name }}
						<el-badge v-if="props.row.available" class="mark" type="success" :value="$lang.buttons.normal" style="margin-left:3px"/>
						<el-badge v-else class="mark" type="danger" :value="$lang.buttons.error" style="margin-left:3px"/>
					</template>
				</el-table-column>
				<el-table-column align="center" :label="$lang.columns.project" width="180">
					<template slot-scope="props">
						<i class="el-icon-document-copy" style="margin-right:6px"></i>
						<span>{{ props.row.project_name }}</span>
					</template>
				</el-table-column>
				<el-table-column align="center" prop="manual" :label="$lang.columns.runMode" width="200">
					<template slot-scope="props">
						<span v-if="props.row.manual" style="color:#9c9c9c; margin-right:8px;">{{ $lang.selects.manual }}</span>
						<span v-else style="color:#9c9c9c; margin-right:8px;">{{ $lang.selects.auto }}</span>
						<el-switch
								v-model="spiders[props.$index].manual"
								active-color="#E6A23C"
								inactive-color="#60BCFE"
								:active-value="true"
								:inactive-value="false"
								@change="onSpiderRunModeUpdte(props.row)">
						</el-switch>
					</template>
				</el-table-column>
				<el-table-column align="center" :label="$lang.columns.nextTime" width="250">
					<template slot-scope="props">
						<el-progress :percentage="calculatePercent(props.row)" color="#35CBAA" :show-text="false"></el-progress>
					</template>
				</el-table-column>
				<el-table-column align="center" :label="$lang.columns.status" width="180">
					<template slot-scope="props">
						<span v-if="spidersStatus[props.row.id] === 2" style="color:#409EFF; font-weight:bold">
							<i class="fa fa-circle" style="margin-right:5px"></i>
							{{ $lang.buttons.finished }}
						</span>
						<span v-else-if="spidersStatus[props.row.id] === 1" style="color:#67C23A; font-weight:bold">
							<i class="el-icon-loading" style="margin-right:5px"></i>
							{{ $lang.buttons.running }}
						</span>
						<span v-else-if="spidersStatus[props.row.id] === 0" style="color:#E6A23C; font-weight:bold">
							<i class="el-icon-loading" style="margin-right:5px"></i>
							{{ $lang.buttons.connecting }}
						</span>
						<span v-else-if="spidersStatus[props.row.id] === -1" style="color:#E6A23C; font-weight:bold">
							<i class="el-icon-loading" style="margin-right:5px"></i>
							{{ $lang.buttons.pending }}
						</span>
						<span v-else style="color:#F56C6C; font-weight:bold">
							<i class="fa fa-circle" style="margin-right:5px"></i>
							{{ $lang.buttons.noJob }}
						</span>
					</template>
				</el-table-column>
				<el-table-column align="center" :label="$lang.columns.operations">
					<template slot-scope="props">
						<el-tooltip :content="$lang.tags.run" placement="top">
							<el-button type="text" size="mini" icon="fa fa-play fa-2x" style="color:#35CBAA" @click="onStartSpider(props.row.id)" :disabled="operationsEnable('run', props.row)"/>
						</el-tooltip>
						<span style="margin-right:40px;"></span>
						<el-tooltip :content="$lang.tags.cancel" placement="top">
							<el-button type="text" size="mini" icon="fa fa-times fa-2x" style="color:#EF6372" @click="onCancelJob(props.row.id)" :disabled="operationsEnable('cancel', props.row)"/>
						</el-tooltip>
						<span style="margin-right:40px;"></span>
						<el-tooltip :content="$lang.tags.intervals" placement="top">
							<el-button type="text" size="mini" icon="fa el-icon-alarm-clock fa-2x" style="color:#606266" @click="onJobIntervals(props.row)"/>
						</el-tooltip>
						<span style="margin-right:40px;"></span>
						<router-link :to="{name: 'SpiderMonitor', params: {spiderInfo: props.row}}" tag="span">
							<el-tooltip :content="$lang.tags.monitor" placement="top">
								<i class="fa-2x el-icon-notebook-2"></i>
							</el-tooltip>
						</router-link>
					</template>
				</el-table-column>
			</el-table>
		</div>
	</div>
</template>

<script>
	import PanelTitle from '../../components/PanelTitle'

	export default {
		name: 'SpiderIndex',
		data() {
			return {
				keyword: '',
				intervalsDialog: false,
				intervals: {},
				currentID: null,
				spiders: null,
				loading: true,
				spidersStatus: {},
				clientId: this.$route.params.id,
				operationEnable: {
					'2': [false, true],
					'1': [true, false],
					'0': [true, true],
					'-1': [true, false],
					'-2': [false, true]
				}
			}
		},
		components: {
			PanelTitle,
		},
		created() {
			this.onGetSpiderData();
			this.$store.commit(
					'addInterval',
					setInterval(() => {
						this.onRefreshSpidersStatus()
					}, 5000)
			)
		},
		methods: {
			onRefresh() {
				this.onGetSpiderData()
			},
			onGetSpidersStatus() {
				this.spiders.forEach((spider) => {
					this.onGetSpiderStatus(spider.id)
				})
			},
			onGetSpiderStatus(id) {
				this.$set(this.spidersStatus, id, 0);
				this.$http.get(this.formatString(this.$store.state.url.spider.status, {
					id: id
				})).then(({data: {status: result}}) => {
					this.$set(this.spidersStatus, id, parseInt(result));
				}).catch(() => {
					this.$set(this.spidersStatus, id, -2)
				})
			},
			onGetSpiderData() {
				this.loading = true;
				this.$http.get(this.formatString(this.$store.state.url.client.listSpiders, {
					id: this.clientId,
					keyword: this.keyword,
				})).then(({data: spiders}) => {
					this.spiders = spiders;
					this.onGetSpidersStatus();
					this.loading = false
				}).catch(() => {
					this.loading = false
				})
			},
			onRefreshSpidersStatus() {
				this.spiders.forEach((spider) => {
					this.$http.get(this.formatString(this.$store.state.url.spider.status, {
						id: spider.id
					})).then(({data: {status: result}}) => {
						this.$set(this.spidersStatus, spider.id, parseInt(result));
					}).catch(() => {
						this.$set(this.spidersStatus, spider.id, -2)
					})
				})
			},
			onSpiderUpdate(id, data) {
				this.loading = true;
				this.$http.post(
						this.formatString(this.$store.state.url.spider.update, {id: id}),
						data
				).then(() => {
					this.$message.success(this.$store.getters.$lang.messages.successSave);
					this.onRefresh()
				}).catch(() => {
					this.$message.error(this.$store.getters.$lang.messages.errorSave);
					this.loading = false
				})
			},
			onSpiderRunModeUpdte(row) {
				if (row.next_run_duration){
					const data = {'manual': row.manual};
					this.onSpiderUpdate(row.id, data)
				} else {
					row.manual = !row.manual;
					this.$message.error(this.$store.getters.$lang.messages.provideInterval);
				}
			},
			onSpiderIntervalsUpdte() {
				const data = {'next_run_duration': this.intervals};
				this.onSpiderUpdate(this.currentID, data);
				this.intervalsDialog = false;
			},
			onStartSpider(id) {
				this.loading = true;
				this.$http.get(this.formatString(this.$store.state.url.spider.start, {
					id: id
				})).then(() => {
					this.$message.success(this.$store.getters.$lang.messages.successRun);
					this.onRefresh()
				}).catch(() => {
					this.$message.error(this.$store.getters.$lang.messages.errorRun);
					this.loading = false
				})
			},
			onCancelJob(id) {
				this.loading = true;
				this.$http.get(this.formatString(this.$store.state.url.spider.cancelJob, {
					id: id
				})).then(() => {
					this.$message.success(this.$store.getters.$lang.messages.canceling);
					this.onRefresh()
				}).catch(() => {
					this.$message.error(this.$store.getters.$lang.messages.errorCancel);
					this.loading = false
				})
			},
			calculatePercent(row) {
				const latest = row.latest_run;
				const duration = row.next_run_duration;
				if (!latest || !duration || row.manual || !row.available) {
					return 0
				}
				const now = new Date();
				const latest_run = new Date(latest);
				const now_duration = now.getTime() - latest_run.getTime();
				const days = Math.floor(now_duration / (24 * 3600 * 1000));
				return Math.floor(days / parseInt(duration) * 100);
			},
			operationsEnable(type, row){
				if(!row.manual){
					return true
				}
				const status = this.spidersStatus[row.id];
				if(type === 'run'){
					return this.operationEnable[status.toString()][0]
				} else {
					return this.operationEnable[status.toString()][1]
				}
			},
			onJobIntervals(row){
				this.currentID = row.id;
				this.intervals = row.next_run_duration;
				this.intervalsDialog = true;
			},
			tableRowClassName(data) {
				if (!data.row.available) {
					return 'warning-row';
				}
				return '';
			}
		}
	}
</script>

<style>
	.el-button:disabled{
		color: #e8ebf1 !important;
	}

	.item {
		margin-top: 5px;
		margin-right: 40px;
	}

	.el-table .warning-row {
		background: oldlace;
	}
</style>