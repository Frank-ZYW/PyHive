<template>
    <div id="task-status">
        <el-dialog :visible.sync="logDialog" size="tiny" width="1050px" class="dialog">
            <div class="panel">
                <panel-title :title="$lang.objects.log"/>
                <div class="panel-body" v-loading="logLoading" style="height:400px;overflow:auto">
                    <pre>{{ logs[logLoadingActive] }}</pre>
                </div>
            </div>
            <div slot="footer">
                <el-button type="primary" @click="logDialog=false" size="small">
                    <i class="fa fa-reply"></i>
                    {{ $lang.buttons.return }}
                </el-button>
            </div>
        </el-dialog>

        <el-row :gutter="20">
            <el-col :span="6">
                <div class="panel">
                    <panel-title :title="$lang.objects.task"></panel-title>
                    <div class="panel-body" style="height:260px">
                        <el-form label-width="110px">
                            <el-form-item :label="$lang.columns.spider">
                                <template>
                                    {{ spiderInfo.name }}
                                    <el-badge v-if="spiderInfo.available" class="mark" type="success" :value="$lang.buttons.normal" style="margin-left:3px"/>
                                    <el-badge v-else class="mark" type="danger" :value="$lang.buttons.error" style="margin-left:3px"/>
                                </template>
                            </el-form-item>
                            <el-form-item :label="$lang.columns.project">{{ spiderInfo.project_name }}</el-form-item>
                            <el-form-item :label="$lang.columns.lastTime">{{ spiderInfo.latest_run }}</el-form-item>
                            <el-form-item :label="$lang.columns.intervals">{{ spiderInfo.next_run_duration }}</el-form-item>
                            <el-form-item :label="$lang.columns.nextTime">
                                <el-progress :percentage="calculatePercent(spiderInfo.latest_run, spiderInfo.next_run_duration)"
                                             color="#35CBAA" style="margin-top: 13px">
                                </el-progress>
                            </el-form-item>
                        </el-form>
                    </div>
                </div>
            </el-col>
            <el-col :span="18">
                <el-row>
                    <el-col :span="24">
                        <div class="panel">
                            <panel-title :title="$lang.objects.logs"/>
                            <div class="panel-body" v-loading="loading">
                                <div class="infinite-list-wrapper" style="height:260px;overflow:auto">
                                    <el-timeline v-if="jobs.length">
                                        <el-timeline-item v-for="(job, index) in jobs" :key="index"
                                                          :timestamp="job.start_time.substring(0,19)"
                                                          placement="top" :type="jobStatusClass[job.status]">
                                            <span v-if="job.spider" class="m-l-md" :style="{minWidth: '290px'}">
                                                <i class="fa fa-key"></i>
                                                {{ $lang.columns.jobID }} : {{ job.id }}
                                            </span>
                                            <span v-if="job.end_time" class="m-l-md" :style="{minWidth: '190px'}">
                                                <i class="el-icon-time"></i>
                                                {{ $lang.columns.endTime }} : {{ job.end_time.substring(0, 19) }}
                                            </span>
                                            <span class="m-l-md">
                                                <el-button :type="jobStatusClass[job.status]" size="mini">
                                                    <i v-if="['pending'].includes(job.status)" class="fa fa-circle-thin"></i>
                                                    <i v-if="['running'].includes(job.status)" class="fa fa-spin fa-spinner"></i>
                                                    <i v-if="['finished'].includes(job.status)" class="fa fa-check"></i>
                                                    {{ jobStatusText[job.status] }}
                                                </el-button>
                                            </span>
                                            <span class="m-l-md">
                                                <el-button type="text" size="mini" class="pull-right m-r-md" @click="onGetLog(job.id)">
                                                    <a style="text-decoration: underline">{{ $lang.buttons.viewLog }}</a>
                                                </el-button>
                                            </span>
                                        </el-timeline-item>
                                    </el-timeline>
                                    <el-table v-else :data="null" :empty-text="$lang.messages.noData" style="height:260px;overflow:auto"></el-table>
                                </div>
                            </div>
                        </div>
                    </el-col>
                </el-row>
            </el-col>
        </el-row>
        <div class="panel">
            <panel-title :title="$lang.titles.thirtyDayOperation">
                <el-button @click="getMonitor" size="mini">
                    <i class="fa fa-refresh"></i>
                    {{ $lang.buttons.refresh }}
                </el-button>
            </panel-title>
            <div class="panel-body" v-loading="!monitorLoading">
                <div v-if="monitorLoading"><ve-histogram :data="monitor" :settings="chartSettings"></ve-histogram></div>
            </div>
        </div>
    </div>
</template>

<script>
    import PanelTitle from '../../components/PanelTitle'

    export default {
        name: "SpiderMonitor",
        data() {
            return {
                errorCount: 0,
                loading: null,
                jobs: {},
                jobStatusClass: {
                    finished: 'info',
                    running: 'success',
                    pending: 'warning'
                },
                jobStatusText: {
                    finished: this.$store.getters.$lang.buttons.finished,
                    running: this.$store.getters.$lang.buttons.running,
                    pending: this.$store.getters.$lang.buttons.pending
                },
                logs: {},
                logLoading: null,
                // tag of timing-refresh log
                logLoadingInterval: null,
                // tag of loading log
                logLoadingActive: null,
                logDialog: false,
                // v-charts config & data
                chartSettings: {},
                monitorLoading: false,
                monitor: {}, // 30-day running record
                // spider info
                spiderInfo: this.$route.params.spiderInfo,
            }
        },
        components: {
            PanelTitle
        },
        created() {
            this.monitor.columns = ['run_date', 'page_ignore', 'run_times',
                'page_error', 'item_scrape', 'item_error'];
            this.chartSettings = {
                dimension: ['run_date'],
                showLine: ['run_times'],
                axisSite: {right: ['run_times']},
                scale: [true, true],
                stack: {'record': ['page_ignore', 'page_error', 'item_scrape', 'item_error']},
                max: ['dataMax', 5],
                labelMap: {
                    'run_date': this.$lang.charts.runDate,
                    'page_ignore': this.$lang.charts.pageIgnore,
                    'page_error': this.$lang.charts.pageError,
                    'item_scrape': this.$lang.charts.itemScrape,
                    'item_error': this.$lang.charts.itemError,
                    'run_times': this.$lang.charts.runTimes
                }
            };
            this.getJobs();
            this.getMonitor();
            this.$store.commit(
                'addInterval',
                setInterval(() => {
                    this.getJobs()
                }, 5000)
            )
        },
        methods: {
            getJobs() {
                this.loading = true;
                this.errorCount = 0;
                this.$http.get(this.formatString(this.$store.state.url.spider.listJobs, {
                    id: this.spiderInfo.id
                })).then(({data: data}) => {
                    this.jobs = data;
                    this.loading = false;
                }).catch(() => {
                    this.loading = false;
                    this.errorCount += 1;
                    if (this.errorCount >= 3) {
                        this.$message.error(this.$store.getters.$lang.messages.errorLoad)
                    } else {
                        this.$store.commit(
                            'setTimeout',
                            setTimeout(() => {
                                this.getJobs()
                            }, 3000)
                        )
                    }
                })
            },
            getLog(job) {
                // log open
                if (job) {
                    this.logLoading = true;
                    this.logLoadingActive = job;
                    this.$http.get(this.formatString(this.$store.state.url.spider.getLog, {
                        id: this.spiderInfo.id,
                        job: this.logLoadingActive
                    })).then(({data: data}) => {
                        this.$set(this.logs, this.logLoadingActive, data);
                        this.logLoading = false;
                        this.$store.commit(
                            'setTimeout',
                            setTimeout(() => {
                                this.getLog(job)
                            }, 2000)
                        )
                    }).catch(() => {
                        this.logLoading = false
                    })
                } else {
                    this.$store.commit('clearTimeout')
                }
            },
            onGetLog(id) {
                this.logDialog = true;
                this.getLog(id);
            },
            getMonitor() {
                this.monitorLoading = false;
                this.$http.get(this.formatString(this.$store.state.url.spider.getMonitor, {
                    id: this.spiderInfo.id,
                })).then(({data: data}) => {
                    this.monitor.rows = data;
                    this.monitorLoading = true;
                }).catch(() => {
                    this.monitorLoading = true;
                })
            },
            calculatePercent(latest, duration) {
                if (!latest || !duration || !this.spiderInfo.available || this.spiderInfo.manual) {
                    return 0
                }
                const now = new Date();
                const latest_run = new Date(latest);
                const now_duration = now.getTime() - latest_run.getTime();
                const days = Math.floor(now_duration / (24 * 3600 * 1000));
                return Math.floor(days / parseInt(duration) * 100);
            }
        }
    }
</script>