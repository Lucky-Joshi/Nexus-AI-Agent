import re
from typing import Dict, Any
from core.logger import Logger


class Router:
    """
    Intent detection and command routing for NEXUS.
    Three-stage routing: regex patterns -> fuzzy matching -> LLM understanding.
    """

    def __init__(self, use_llm: bool = True, llm_provider=None):
        self.logger = Logger().get_logger("Router")
        self._routing_rules = self._build_rules()
        self._use_llm = use_llm
        self._llm = llm_provider
        self._agent_descriptions = self._build_agent_descriptions()

    def _build_agent_descriptions(self) -> str:
        return """Available agents and their capabilities:
- file_agent: open apps/files/folders, create/delete/rename files, search files, system info (cpu/ram/disk), kill processes, organize downloads
- web_agent: search web, scrape pages, summarize URLs/articles, research topics, compare options, extract keywords
- automation_agent: screenshots, mouse/keyboard automation, run workflows (coding_mode, study_mode, etc), hotkeys
- coding_agent: generate/explain/debug code, git operations, analyze repositories, run commands, edit files
- memory_agent: remember facts, recall memories, save/get preferences, save/load workflows, manage context, list memories
- plugin_agent: install/uninstall/enable/disable plugins, list plugins, plugin security, run plugin commands, discover plugins
- security_agent: analyze commands for risks, system health checks, process scanning, security monitoring, audit logs, permission management, file protection
- workflow_chain_agent: chain multiple agents together, pass outputs between agents, run multi-step workflows, execute chain templates, prepare coding workspace, research and summarize
- analytics_agent: system usage analytics, agent performance tracking, productivity metrics, resource monitoring, dashboard, reports
- context_awareness_agent: detect user activity, monitor focus levels, suggest workflows based on context, adaptive triggers, running apps detection, window tracking
- learning_agent: track user behavior, detect patterns and habits, generate recommendations, predict next actions, learn from interactions, adaptive workflow generation
- communication_bus_agent: inter-agent messaging, event publishing/broadcasting, pub/sub subscriptions, shared state management, event logging, message tracking, dead letter queue, communication statistics
- planner_agent: break goals into multi-step plans, autonomous task execution across agents, dependency resolution, dynamic replanning, goal templates, progress tracking, parallel task execution
- marketplace_agent: browse and install community agents, agent verification and security scanning, dependency resolution, ratings and reviews, update management, sandboxed installation"""


    def _build_rules(self) -> list:
        return [
            {
                "patterns": [
                    r"\b(open)\b.*\b(desktop|downloads|documents|pictures|videos|onedrive)\b",
                ],
                "agent": "file_agent",
                "intent": "open_folder",
            },
            {
                "patterns": [
                    r"\b(open|find)\b.*\b(pdf)\b",
                ],
                "agent": "file_agent",
                "intent": "open_pdf",
            },
            {
                "patterns": [
                    r"\b(open|find|play)\b.*\b(media|video|music|mp4|mp3)\b",
                ],
                "agent": "file_agent",
                "intent": "open_media",
            },
            {
                "patterns": [
                    r"\b(screenshot|screen capture|capture screen|take screenshot)\b",
                    r"\b(ocr|read text|extract text|text from screen)\b",
                    r"\b(find text|search text|look for text)\b.*\b(screen)\b",
                    r"\b(active window|current window|focused window|what window)\b",
                    r"\b(list windows|show windows|all windows|open windows)\b",
                    r"\b(analyze screen|screen analysis|analyze desktop|what.s on screen)\b",
                    r"\b(screen size|screen resolution|display info|monitor info)\b",
                    r"\b(monitor windows|track windows|watch windows|window history)\b",
                    r"\b(screen summary|screen status|desktop status)\b",
                    r"\b(vision|vision status)\b",
                    r"\b(screenshot history|saved screenshots|list screenshots)\b",
                    r"\b(compare screens|screen change|what changed)\b",
                    r"\b(capture region|screenshot region|capture area)\b",
                ],
                "agent": "vision_agent",
                "intent": "vision",
            },
            {
                "patterns": [
                    r"\b(automate|automation|automated)\b",
                    r"\b(click|type|press|key)\b",
                    r"\b(workflows?|preset|sequence|mode)\b",
                    r"\b(mouse|cursor)\b.*\b(move|click|position)\b",
                    r"\b(hotkey|press key)\b",
                ],
                "agent": "automation_agent",
                "intent": "automation",
            },
            {
                "patterns": [
                    r"\b(open|launch|start)\b.*\b(app|application|program|software)\b",
                    r"\b(open|launch|run)\b",
                ],
                "agent": "file_agent",
                "intent": "open_application",
            },
            {
                "patterns": [
                    r"\b(open)\b.*\b(file explorer|explorer)\b",
                ],
                "agent": "file_agent",
                "intent": "open_application",
            },
            {
                "patterns": [
                    r"\b(open)\b.*\b(file)\b",
                    r"\b(open)\b.*\b(document|pdf|image|video|audio)\b",
                ],
                "agent": "file_agent",
                "intent": "open_file",
            },
            {
                "patterns": [
                    r"\b(create|make|new)\b.*\b(files?|folders?|directories?)\b",
                    r"\b(delete|remove|trash)\b",
                    r"\b(rename|move|copy)\b.*\b(files?|folders?)\b",
                    r"\bsearch\b.*\b(files?|folders?|directories?)\b",
                    r"\b(files?|folders?|directories?)\b.*\b(search|find|list)\b",
                    r"\b(list|ls|dir)\b.*\b(folder|directory|contents)\b",
                    r"\b(read|show|view)\b.*\b(file)\b",
                    r"\b(organize)\b.*\b(downloads?)\b",
                    r"\b(cpu|ram|disk|storage|network)\b",
                    r"\b(kill|stop|terminate)\b.*\b(process)\b",
                ],
                "agent": "file_agent",
                "intent": "file_operation",
            },
            {
                "patterns": [
                    r"\b(system|cpu|ram|memory|disk|storage)\b.*\b(info|status|usage|monitor)\b",
                    r"\b(check|show|get)\b.*\b(system|cpu|ram|memory|disk|storage)\b(?!.*\b(safety|security|risk|threat)\b)",
                    r"\bhow much\b.*\b(cpu|ram|memory|disk|storage)\b",
                ],
                "agent": "file_agent",
                "intent": "system_info",
            },
            {
                "patterns": [
                    r"\b(search|find|look up|google)\b.*\b(web|internet|online)\b",
                    r"\b(web|internet)\b.*\b(search|find)\b",
                    r"\b(scrape|extract|fetch)\b.*\b(page|website|url|site)\b",
                    r"\b(summarize|summary)\b.*\b(url|link|page|article|website)\b",
                    r"\b(research|investigate)\b",
                ],
                "agent": "web_agent",
                "intent": "web_search",
            },
            {
                "patterns": [
                    r"\b(code|coding|program|script)\b.*\b(generate|write|create|build)\b",
                    r"\b(generate|write|create)\b.*\b(code|function|class|script)\b",
                    r"\b(debug|fix|error|bug)\b.*\b(code)\b",
                    r"\b(explain)\b.*\b(code|this code|this function)\b",
                    r"\b(git)\b.*\b(commit|push|pull|status|branch|clone)\b",
                    r"\b(analyze)\b.*\b(repository|repo|codebase)\b",
                    r"\b(edit|modify|change)\b.*\b(file|code)\b",
                ],
                "agent": "coding_agent",
                "intent": "coding",
            },
            {
                "patterns": [
                    r"\b(remember|save|store|note)\b",
                    r"\b(recall|retrieve|what did)\b",
                    r"\b(context|history|previous)\b",
                    r"\b(preference|setting)\b.*\b(save|set|change|get)\b",
                    r"\b(save|set|change|get)\b.*\b(preference|setting)\b",
                    r"\b(what do you know|what do you remember)\b",
                    r"\b(list|show)\b.*\b(memories|preferences|workflows)\b",
                    r"\b(memory|memories)\b.*\b(stats|status|list|clear)\b",
                    r"\b(save|create|load|run|execute)\b.*\b(workflow)\b",
                    r"\b(delete|forget|remove)\b.*\b(memory|memories)\b",
                ],
                "agent": "memory_agent",
                "intent": "memory",
            },
            {
                "patterns": [
                    r"\b(screenshot|screen capture|capture screen|take screenshot)\b",
                    r"\b(ocr|read text|extract text|text from screen)\b",
                    r"\b(find text|search text|look for text)\b.*\b(screen)\b",
                    r"\b(active window|current window|focused window|what window)\b",
                    r"\b(list windows|show windows|all windows|open windows)\b",
                    r"\b(analyze screen|screen analysis|analyze desktop|what.s on screen)\b",
                    r"\b(screen size|screen resolution|display info|monitor info)\b",
                    r"\b(monitor windows|track windows|watch windows|window history)\b",
                    r"\b(screen summary|screen status|desktop status)\b",
                    r"\b(vision|vision status)\b",
                    r"\b(screenshot history|saved screenshots|list screenshots)\b",
                    r"\b(compare screens|screen change|what changed)\b",
                    r"\b(capture region|screenshot region|capture area)\b",
                ],
                "agent": "vision_agent",
                "intent": "vision",
            },
            {
                "patterns": [
                    r"\b(send notification|notify|show notification|popup)\b",
                    r"\b(set reminder|remind me|reminder|alarm)\b",
                    r"\b(focus mode|silent mode|do not disturb|dnd)\b",
                    r"\b(notification status|notification stats|notification info)\b",
                    r"\b(pending notifications|pending alerts|queue)\b",
                    r"\b(notification history|alert history|past notifications)\b",
                    r"\b(clear notifications|clear queue|dismiss all)\b",
                    r"\b(dismiss notification|dismiss alert)\b",
                    r"\b(test notification|test alert|test popup)\b",
                    r"\b(scheduled reminders|pending reminders|upcoming reminders)\b",
                    r"\b(cancel reminder|remove reminder)\b",
                    r"\b(agent alert|alert agent|agent notification)\b",
                    r"\b(workflow alert|workflow notification|workflow complete)\b",
                    r"\b(set priority)\b.*\b(notification)\b",
                ],
                "agent": "notification_agent",
                "intent": "notification",
            },
            {
                "patterns": [
                    r"\b(schedule|schedule task|create schedule)\b",
                    r"\b(list schedules|list tasks|show schedules|all schedules)\b",
                    r"\b(run now|execute now|run task)\b",
                    r"\b(cancel schedule|delete schedule|remove task)\b",
                    r"\b(pause schedule|pause task)\b",
                    r"\b(resume schedule|resume task)\b",
                    r"\b(schedule status|scheduler status|schedule info)\b",
                    r"\b(execution history|task history|run history)\b",
                    r"\b(schedule reminder|remind me at|remind me every)\b",
                    r"\b(schedule workflow|workflow schedule)\b",
                ],
                "agent": "scheduler_agent",
                "intent": "scheduler",
            },
            {
                "patterns": [
                    r"\b(add document|add note|create document|save knowledge|store document)\b",
                    r"\b(search knowledge|search documents|find document|knowledge search)\b",
                    r"\b(get document|show document|view document|read document)\b",
                    r"\b(delete document|remove document)\b",
                    r"\b(list documents|list knowledge|show all documents)\b",
                    r"\b(add tag|tag document)\b",
                    r"\b(remove tag|untag)\b",
                    r"\b(list tags|show tags|all tags)\b",
                    r"\b(summarize document|summarize|generate summary)\b",
                    r"\b(summarize tag|tag summary)\b",
                    r"\b(index document|index all|rebuild index|reindex)\b",
                    r"\b(import file|import document|load file)\b",
                    r"\b(knowledge stats|knowledge base stats|kb stats)\b",
                    r"\b(recent documents|recent knowledge|latest documents)\b",
                    r"\b(documents by tag|tagged with)\b",
                    r"\b(documents by category|category:)\b",
                    r"\b(knowledge base|knowledge agent)\b",
                ],
                "agent": "knowledge_agent",
                "intent": "knowledge",
            },
            {
                "patterns": [
                    r"\b(run |execute |exec |terminal run|shell run)\b",
                    r"\b(run script|execute script|run file|exec script)\b",
                    r"\b(run python|exec python|python code|run code)\b",
                    r"\b(stream |stream run|stream execute)\b",
                    r"\b(new session|create session|open session|new terminal)\b",
                    r"\b(switch session|use session|select session)\b",
                    r"\b(close session|end session|exit session)\b",
                    r"\b(list sessions|show sessions|all sessions|sessions)\b",
                    r"\b(cd |change dir|change directory|set directory)\b",
                    r"\b(set env|set environment|set variable)\b",
                    r"\b(kill process|kill command|stop command|stop process)\b",
                    r"\b(kill all|stop all|kill all processes)\b",
                    r"\b(command history|history|recent commands|terminal history)\b",
                    r"\b(search history|find command|search commands)\b",
                    r"\b(failed commands|errors|command errors)\b",
                    r"\b(blocked commands|safety log|security log)\b",
                    r"\b(terminal stats|terminal status|stats)\b",
                    r"\b(check command|validate command|is safe)\b",
                    r"\b(clear history|clear terminal|reset history)\b",
                    r"\b(set timeout|timeout)\b",
                    r"\b(strict mode|safety mode)\b",
                    r"\b(force run|force execute|run force)\b",
                    r"\b(pwd|print working directory|current directory|where am i)\b",
                    r"\b(terminal|shell|command line|cmd|powershell)\b",
                ],
                "agent": "terminal_agent",
                "intent": "terminal",
            },
            {
                "patterns": [
                    r"\b(set personality|set persona|switch personality|switch persona)\b",
                    r"\b(list personalities|list personas|show personalities|show personas)\b",
                    r"\b(personality status|persona status|my personality|current personality)\b",
                    r"\b(set tone|change tone|switch tone)\b",
                    r"\b(set humor|humor level|be funny|be serious)\b",
                    r"\b(set formality|formality level|be formal|be casual)\b",
                    r"\b(set verbosity|verbosity level|be brief|be detailed)\b",
                    r"\b(set empathy|empathy level|be empathetic)\b",
                    r"\b(set creativity|creativity level|be creative)\b",
                    r"\b(set confidence|confidence level)\b",
                    r"\b(set emoji|emoji usage|use emoji)\b",
                    r"\b(set slang|slang tolerance|use slang)\b",
                    r"\b(create profile|create personality|new profile)\b",
                    r"\b(list profiles|show profiles|all profiles)\b",
                    r"\b(switch profile|use profile|select profile)\b",
                    r"\b(delete profile|remove profile)\b",
                    r"\b(set user name|my name is|call me)\b",
                    r"\b(set greeting|greeting style)\b",
                    r"\b(set signoff|signoff style)\b",
                    r"\b(emotion status|current emotion|how are you feeling)\b",
                    r"\b(session status|session info|how long talking)\b",
                    r"\b(personality stats|persona stats)\b",
                    r"\b(reset personality|reset persona|default personality)\b",
                    r"\b(transform response|apply personality)\b",
                    r"\b(detect tone|analyze tone|what tone)\b",
                    r"\b(greet|say hello|greeting)\b",
                    r"\b(personality agent|persona agent)\b",
                ],
                "agent": "personality_agent",
                "intent": "personality",
            },
            {
                "patterns": [
                    r"\b(start |activate |enable |launch |open |prepare ).*mode\b",
                    r"\b(stop |deactivate |disable |exit |close ).*mode\b",
                    r"\b(list modes|show modes|all modes|available modes|workflow modes)\b",
                    r"\b(mode status|current mode|active mode|what mode)\b",
                    r"\b(cancel mode|stop mode|abort mode)\b",
                    r"\b(mode history|session history|mode sessions)\b",
                    r"\b(mode stats|workflow stats|productivity stats)\b",
                    r"\b(create mode|new mode|custom mode)\b",
                    r"\b(delete mode|remove mode)\b",
                    r"\b(mode info|mode details|show mode)\b",
                    r"\b(pause mode|resume mode)\b",
                    r"\b(workflow agent|workflow mode)\b",
                    r"\b(coding mode|study mode|deep work mode|content creation mode)\b",
                    r"\b(meeting mode|research mode|cybersecurity mode|design mode)\b",
                    r"\b(writing mode|gaming mode|ai development mode|project management mode)\b",
                ],
                "agent": "workflow_agent",
                "intent": "workflow",
            },
            {
                "patterns": [
                    r"\b(install plugin|add plugin|load plugin)\b",
                    r"\b(uninstall plugin|remove plugin|delete plugin)\b",
                    r"\b(enable plugin|activate plugin|turn on plugin)\b",
                    r"\b(disable plugin|deactivate plugin|turn off plugin)\b",
                    r"\b(reload plugin|hot reload|refresh plugin)\b",
                    r"\b(list plugins|show plugins|all plugins|installed plugins)\b",
                    r"\b(plugin status|plugin info|plugin details)\b",
                    r"\b(plugin commands|plugin capabilities)\b",
                    r"\b(plugin events|plugin history|plugin log)\b",
                    r"\b(plugin stats|plugin diagnostics|plugin health)\b",
                    r"\b(discover plugins|scan plugins|find plugins)\b",
                    r"\b(plugin security|analyze plugin)\b",
                    r"\b(run plugin|execute plugin|plugin run)\b",
                    r"\b(plugin help|plugin guide|how to plugin)\b",
                    r"\b(plugin agent|plugin manager)\b",
                    r"\b(enable .* plugin|disable .* plugin|activate .* plugin|deactivate .* plugin)\b",
                    r"\b(.+ plugin)\b",
                ],
                "agent": "plugin_agent",
                "intent": "plugin",
            },
            {
                "patterns": [
                    r"\b(analyze|check risk|risk check|scan command|security check)\b",
                    r"\b(block|allow|force execute|override)\b",
                    r"\b(system health|health check|system scan|check system|system status|system safety|safety check)\b",
                    r"\b(process scan|scan processes|suspicious process|list suspicious)\b",
                    r"\b(start monitoring|enable monitoring|start monitor|monitor start)\b",
                    r"\b(stop monitoring|disable monitoring|stop monitor|monitor stop)\b",
                    r"\b(events|security events|list events|show events)\b",
                    r"\b(audit|audit log|audit trail|show audit|list audit)\b",
                    r"\b(alerts|security alerts|list alerts|show alerts|active alerts)\b",
                    r"\b(permissions|permission rules|list permissions|show permissions)\b",
                    r"\b(add permission|new permission|create permission)\b",
                    r"\b(remove permission|delete permission)\b",
                    r"\b(file protection|protect file|protect folder|file rules)\b",
                    r"\b(add protection|protect path)\b",
                    r"\b(policy|security policy|show policy|policy status)\b",
                    r"\b(set policy|update policy|change policy)\b",
                    r"\b(stats|security stats|security status|security summary)\b",
                    r"\b(validate workflow|workflow security|check workflow)\b",
                    r"\b(execution log|exec log|run history)\b",
                    r"\b(security agent|security help|security monitor)\b",
                ],
                "agent": "security_agent",
                "intent": "security",
            },
            {
                "patterns": [
                    r"\b(run chain|execute chain|start chain|run workflow|execute workflow)\b",
                    r"\b(run async|execute async|start async)\b",
                    r"\b(cancel chain|stop chain|cancel workflow|stop workflow)\b",
                    r"\b(chain status|workflow status|execution status|chain progress)\b",
                    r"\b(list chains|show chains|all chains|available chains)\b",
                    r"\b(chain info|workflow info|chain details|show chain)\b",
                    r"\b(create chain|new chain|add chain|define chain)\b",
                    r"\b(delete chain|remove chain)\b",
                    r"\b(list templates|show templates|available templates|template list)\b",
                    r"\b(run template|execute template|use template)\b",
                    r"\b(chain history|chain executions|past chain runs|chain execution history)\b",
                    r"\b(chain stats|workflow stats|chain statistics)\b",
                    r"\b(resume chain|resume execution|continue chain)\b",
                    r"\b(prepare coding workspace|setup coding|coding setup)\b",
                    r"\b(research and summarize|research topic|research and report)\b",
                    r"\b(workflow chain|chain agent|chain help)\b",
                    r"\b(chain multiple agents|agent pipeline|agent chain)\b",
                ],
                "agent": "workflow_chain_agent",
                "intent": "workflow_chain",
            },
            {
                "patterns": [
                    r"\b(dashboard|analytics dashboard|system dashboard|overview)\b",
                    r"\b(usage stats|usage statistics|command stats|activity stats)\b",
                    r"\b(agent performance|agent stats|agent metrics|performance report)\b",
                    r"\b(usage report|activity report|command report)\b",
                    r"\b(productivity report|productivity stats|productivity metrics)\b",
                    r"\b(resource monitor|resource stats|resource history|system resources)\b",
                    r"\b(start monitoring|start resource monitoring|enable monitoring)\b",
                    r"\b(stop monitoring|stop resource monitoring|disable monitoring)\b",
                    r"\b(resource snapshot|capture resources|current resources)\b",
                    r"\b(session start|start session|new session|begin session)\b",
                    r"\b(session end|end session|close session|stop session)\b",
                    r"\b(session history|session log|past sessions)\b",
                    r"\b(productivity summary|weekly productivity|monthly productivity)\b",
                    r"\b(top agents|most used agents|agent ranking)\b",
                    r"\b(hourly activity|hourly usage|usage by hour)\b",
                    r"\b(daily activity|daily usage|usage by day)\b",
                    r"\b(recent activity|recent commands|recent usage)\b",
                    r"\b(reports|list reports|show reports|saved reports)\b",
                    r"\b(cleanup|clean data|purge old data)\b",
                    r"\b(analytics|analytics agent|analytics help)\b",
                ],
                "agent": "analytics_agent",
                "intent": "analytics",
            },
            {
                "patterns": [
                    r"\b(current context|what am i doing|what context|my context|detect context)\b",
                    r"\b(active window|current window|focused window|what window)\b",
                    r"\b(running apps|open apps|what apps|list apps|app list)\b",
                    r"\b(activity type|what activity|my activity|detect activity)\b",
                    r"\b(focus level|my focus|am i focused|focus status)\b",
                    r"\b(system load|system status|resource load|cpu load)\b",
                    r"\b(suggest workflow|workflow suggestion|what mode|suggest mode)\b",
                    r"\b(suggest actions|what should i do|recommendations|context suggestions)\b",
                    r"\b(start monitoring|enable monitoring|start context monitor|monitor start)\b",
                    r"\b(stop monitoring|disable monitoring|stop context monitor|monitor stop)\b",
                    r"\b(workflow patterns|detect workflows|workflow detection|pattern list)\b",
                    r"\b(detect workflow|what workflow|current workflow)\b",
                    r"\b(triggers|adaptive triggers|list triggers|trigger list)\b",
                    r"\b(add trigger|new trigger|create trigger)\b",
                    r"\b(toggle trigger|enable trigger|disable trigger)\b",
                    r"\b(context history|context log|past context|context timeline)\b",
                    r"\b(activity summary|activity stats|usage summary|activity report)\b",
                    r"\b(session start|start session|new session)\b",
                    r"\b(session end|end session|close session)\b",
                    r"\b(context rules|list rules|show rules)\b",
                    r"\b(add rule|new rule|create rule)\b",
                    r"\b(delete rule|remove rule)\b",
                    r"\b(cleanup|clean context|purge context)\b",
                    r"\b(context|context agent|context help)\b",
                ],
                "agent": "context_awareness_agent",
                "intent": "context",
            },
            {
                "patterns": [
                    r"\b(learn|start learning|enable learning|learning on)\b",
                    r"\b(stop learning|disable learning|learning off)\b",
                    r"\b(analyze|analyze patterns|run analysis|learn now)\b",
                    r"\b(patterns|learned patterns|show patterns|list patterns)\b",
                    r"\b(habits|my habits|detected habits|habit list)\b",
                    r"\b(recommendations|recommendations for me|suggestions|what should i do)\b",
                    r"\b(accept recommendation|accept suggestion|apply recommendation)\b",
                    r"\b(dismiss recommendation|dismiss suggestion|ignore recommendation)\b",
                    r"\b(predict|predict next|what next|next action)\b",
                    r"\b(behavior history|my behaviors|behavior log|action history)\b",
                    r"\b(learning stats|learning statistics|learning status|how much learned)\b",
                    r"\b(generate workflow|create workflow|workflow from pattern|auto workflow)\b",
                    r"\b(daily routine|morning routine|generate routine|my routine)\b",
                    r"\b(most common|frequent actions|top actions|common actions)\b",
                    r"\b(hourly pattern|activity by hour|when am i active)\b",
                    r"\b(daily pattern|activity by day|which day active)\b",
                    r"\b(prediction accuracy|how accurate|prediction stats)\b",
                    r"\b(cleanup|clean learning data|purge old data)\b",
                    r"\b(learning|learning agent|learning help)\b",
                ],
                "agent": "learning_agent",
                "intent": "learning",
            },
            {
                "patterns": [
                    r"\b(publish|emit event|send event|broadcast event)\b",
                    r"\b(broadcast|broadcast to all|send to all)\b",
                    r"\b(send message|direct message|dm agent)\b",
                    r"\b(subscribe|listen to|subscribe to event)\b",
                    r"\b(unsubscribe|remove subscription|stop listening)\b",
                    r"\b(list subscriptions|show subscriptions|my subscriptions)\b",
                    r"\b(shared state|shared memory|inter-agent state)\b",
                    r"\b(set state|update shared state|write state)\b",
                    r"\b(get state|read shared state|read state)\b",
                    r"\b(delete state|remove shared state|clear state)\b",
                    r"\b(lock state|lock key|lock entry)\b",
                    r"\b(unlock state|unlock key|unlock entry)\b",
                    r"\b(list state|show all state|state list)\b",
                    r"\b(event logs|event history|bus logs|message logs)\b",
                    r"\b(event summary|bus summary|communication summary)\b",
                    r"\b(agent activity|agent communication activity)\b",
                    r"\b(communication flow|message flow|agent flow)\b",
                    r"\b(error report|bus errors|communication errors)\b",
                    r"\b(bus stats|communication stats|bus statistics)\b",
                    r"\b(message status|check message|delivery status)\b",
                    r"\b(dlq|dead letter|dlq messages|dead letter queue)\b",
                    r"\b(retry dlq|retry failed message)\b",
                    r"\b(purge dlq|clear dlq|empty dead letter)\b",
                    r"\b(registered agents|agents on bus|bus agents)\b",
                    r"\b(communication bus|comm bus|message bus|event bus)\b",
                ],
                "agent": "communication_bus_agent",
                "intent": "communication_bus",
            },
            {
                "patterns": [
                    r"\b(plan|create plan|make plan|generate plan|build plan)\b",
                    r"\b(start plan|execute plan|run plan|begin plan)\b",
                    r"\b(stop plan|halt plan|end plan)\b",
                    r"\b(pause plan|resume plan)\b",
                    r"\b(cancel plan|abort plan)\b",
                    r"\b(plan status|check plan|plan info|plan details)\b",
                    r"\b(plan progress|how far along|plan completion)\b",
                    r"\b(list plans|show plans|my plans|all plans)\b",
                    r"\b(active plans|current plans|running plans)\b",
                    r"\b(plan history|plan log|execution history)\b",
                    r"\b(replan|re-plan|redo plan|adjust plan|modify plan)\b",
                    r"\b(templates|goal templates|plan templates|blueprint)\b",
                    r"\b(add template|new template|create template)\b",
                    r"\b(planner stats|planning stats|planner statistics)\b",
                    r"\b(prepare for|get ready for|set up for|organize for)\b",
                    r"\b(break down|decompose|split into steps|step by step)\b",
                    r"\b(autonomous|auto execute|auto plan|automate task)\b",
                    r"\b(planner|planner agent|planning agent|task planner)\b",
                ],
                "agent": "planner_agent",
                "intent": "planner",
            },
            {
                "patterns": [
                    r"\b(browse|browse marketplace|browse agents|browse catalog)\b",
                    r"\b(search marketplace|search agents|find agent|find agents)\b",
                    r"\b(featured|featured agents|popular agents|trending)\b",
                    r"\b(categories|agent categories|browse categories)\b",
                    r"\b(agent info|agent details|agent information|view agent)\b",
                    r"\b(install agent|install marketplace|get agent|add agent)\b",
                    r"\b(uninstall agent|remove agent|delete agent|remove marketplace)\b",
                    r"\b(update agent|upgrade agent|update marketplace)\b",
                    r"\b(check updates|check for updates|available updates)\b",
                    r"\b(installed|installed agents|my agents|my installed)\b",
                    r"\b(enable agent|disable agent|enable marketplace|disable marketplace)\b",
                    r"\b(review|write review|rate agent|leave review)\b",
                    r"\b(reviews|read reviews|agent reviews|user reviews)\b",
                    r"\b(verify|verify agent|security check|check security)\b",
                    r"\b(dependency tree|show dependencies|agent dependencies)\b",
                    r"\b(marketplace stats|marketplace statistics|store stats)\b",
                    r"\b(marketplace|agent store|plugin store|app store)\b",
                ],
                "agent": "marketplace_agent",
                "intent": "marketplace",
            },
        ]

    def detect_intent(self, command: str) -> Dict[str, Any]:
        """
        Detect the intent of a user command and route to the appropriate agent.
        Three-stage routing:
        1. Regex pattern matching (fast, exact)
        2. Fuzzy keyword matching (handles typos)
        3. LLM understanding (handles natural language, severe typos)
        Returns: {agent, intent, confidence, params}
        """
        command_lower = command.lower().strip()

        if not command_lower:
            return {
                "agent": None,
                "intent": "unknown",
                "confidence": 0.0,
                "params": {},
            }

        if command_lower in ("help", "what can you do", "capabilities"):
            return {
                "agent": "manager",
                "intent": "help",
                "confidence": 1.0,
                "params": {},
            }

        if command_lower in ("status", "system status", "agent status"):
            return {
                "agent": "manager",
                "intent": "status",
                "confidence": 1.0,
                "params": {},
            }

        if command_lower in ("clear", "clear chat", "clear conversation"):
            return {
                "agent": "manager",
                "intent": "clear",
                "confidence": 1.0,
                "params": {},
            }

        # Stage 1: Regex pattern matching
        best_match = self._regex_match(command_lower)
        if best_match and best_match["confidence"] >= 0.8:
            self.logger.info(
                f"Routed to {best_match['agent']} (intent: {best_match['intent']}, confidence: {best_match['confidence']:.2f})"
            )
            return best_match

        # Stage 2: Fuzzy keyword matching
        fuzzy_match = self._fuzzy_match(command_lower)
        if fuzzy_match and fuzzy_match["confidence"] > 0.65:
            self.logger.info(
                f"Fuzzy routed to {fuzzy_match['agent']} (intent: {fuzzy_match['intent']}, confidence: {fuzzy_match['confidence']:.2f})"
            )
            return fuzzy_match

        # Stage 3: LLM understanding (handles typos and natural language)
        if self._use_llm and self._llm and self._llm.is_available():
            llm_match = self._llm_route(command)
            if llm_match:
                if not best_match or llm_match["confidence"] > best_match["confidence"]:
                    self.logger.info(
                        f"LLM routed to {llm_match['agent']} (intent: {llm_match['intent']}, confidence: {llm_match['confidence']:.2f})"
                    )
                    return llm_match

        if best_match:
            self.logger.info(
                f"Routed to {best_match['agent']} (intent: {best_match['intent']}, confidence: {best_match['confidence']:.2f})"
            )
            return best_match

        self.logger.warning(f"No routing rule matched for: {command}")
        return {
            "agent": "unknown",
            "intent": "conversation",
            "confidence": 0.0,
            "params": {"original_command": command},
        }

    def _regex_match(self, command_lower: str) -> Dict[str, Any]:
        """Stage 1: Match using regex patterns."""
        best_match = None
        best_confidence = 0.0

        for rule in self._routing_rules:
            for pattern in rule["patterns"]:
                match = re.search(pattern, command_lower)
                if match:
                    confidence = self._calculate_confidence(match, command_lower)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = {
                            "agent": rule["agent"],
                            "intent": rule["intent"],
                            "confidence": confidence,
                            "params": self._extract_params(command_lower, match),
                        }

        return best_match

    def _fuzzy_match(self, command_lower: str) -> Dict[str, Any]:
        """Stage 2: Fuzzy keyword matching for typo tolerance."""
        from difflib import get_close_matches

        command_words = set(re.findall(r"\b[a-z]{3,}\b", command_lower))
        if not command_words:
            return None

        agent_keywords = {
            "file_agent": {
                "keywords": ["notepad", "calculator", "explorer", "desktop", "downloads", "documents",
                             "pictures", "videos", "onedrive", "folder", "directory", "file", "app",
                             "application", "program", "software", "cpu", "ram", "disk", "memory",
                             "storage", "network", "process", "system", "rename", "delete", "remove",
                             "copy", "move", "organize", "kill", "terminate", "pdf", "media", "music"],
                "intent": "file_operation",
            },
            "web_agent": {
                "keywords": ["search", "web", "internet", "online", "google", "duckduckgo", "scrape", "extract",
                             "fetch", "summarize", "summary", "research", "investigate", "compare", "keywords",
                             "page", "website", "url", "site", "article", "link", "browse", "http"],
                "intent": "web_search",
            },
            "automation_agent": {
                "keywords": ["automate", "automation", "automated", "click", "type", "press", "key", "workflow",
                             "preset", "sequence", "screenshot", "screen", "capture", "mouse", "cursor",
                             "hotkey", "macro", "record", "playback"],
                "intent": "automation",
            },
            "coding_agent": {
                "keywords": ["code", "coding", "program", "script", "generate", "write", "build",
                             "debug", "fix", "error", "bug", "explain", "function", "class", "git", "commit",
                             "push", "pull", "branch", "clone", "analyze", "repository", "repo",
                             "codebase", "edit", "modify", "execute", "test", "python", "javascript", "html"],
                "intent": "coding",
            },
            "memory_agent": {
                "keywords": ["remember", "recall", "retrieve", "context", "history",
                             "previous", "preference", "setting", "memory", "memories", "workflow", "workflows",
                             "know", "forget", "clear", "stats", "note", "store"],
                "intent": "memory",
            },
            "knowledge_agent": {
                "keywords": ["knowledge", "document", "documents", "article", "research", "note", "notes",
                             "tag", "tags", "index", "semantic", "search", "summarize", "summary",
                             "import", "database", "library", "archive", "reference", "wiki",
                             "store", "save", "retrieve", "find", "categorize", "organize"],
                "intent": "knowledge",
            },
            "terminal_agent": {
                "keywords": ["terminal", "shell", "command", "run", "execute", "exec", "stream",
                             "session", "script", "python", "history", "kill", "stop", "cd",
                             "directory", "environment", "timeout", "safety", "validate", "force",
                             "pwd", "cmd", "powershell", "bash", "console"],
                "intent": "terminal",
            },
            "personality_agent": {
                "keywords": ["personality", "persona", "tone", "humor", "funny", "serious", "formal",
                             "casual", "empathy", "empathetic", "creativity", "creative", "confidence",
                             "emoji", "slang", "greeting", "signoff", "emotion", "feeling", "mood",
                             "style", "verbose", "brief", "detailed", "preset", "profile"],
                "intent": "personality",
            },
            "workflow_agent": {
                "keywords": ["workflow", "mode", "coding", "study", "deep work", "focus", "meeting",
                             "research", "cybersecurity", "design", "writing", "gaming", "ai development",
                             "project management", "content creation", "activate", "enable", "launch",
                             "productivity", "environment", "workspace", "timer", "pomodoro"],
                "intent": "workflow",
            },
            "plugin_agent": {
                "keywords": ["plugin", "plugins", "extension", "addon", "add-on", "module",
                             "install", "uninstall", "enable", "disable", "load", "unload",
                             "reload", "sandbox", "registry", "capability", "capabilities"],
                "intent": "plugin",
            },
            "security_agent": {
                "keywords": ["security", "analyze", "risk", "threat", "dangerous", "block",
                             "permission", "permissions", "audit", "monitor", "monitoring",
                             "health check", "system health", "process scan", "suspicious",
                             "alert", "alerts", "policy", "protection", "safe", "unsafe",
                             "firewall", "malware", "virus", "scan", "vulnerability",
                             "execution log", "security stats", "security status"],
                "intent": "security",
            },
            "workflow_chain_agent": {
                "keywords": ["chain", "chains", "workflow chain", "agent chain", "pipeline",
                             "run chain", "execute chain", "chain status", "chain template",
                             "coding workspace", "research and summarize",
                             "chain stats", "chain history", "chain progress",
                             "multi-agent", "agent pipeline", "chain execution",
                             "resume chain", "cancel chain", "chain info",
                             "chain steps", "chain dependencies", "chain output",
                             "chain executions", "past chain runs"],
                "intent": "workflow_chain",
            },
            "analytics_agent": {
                "keywords": ["analytics", "dashboard", "usage", "statistics", "stats",
                             "performance", "metrics", "report", "reports", "productivity",
                             "resource monitor", "resource usage", "system resources",
                             "session", "sessions", "activity", "hourly", "daily",
                             "top agents", "agent ranking", "focus score",
                             "cleanup", "analytics dashboard", "overview"],
                "intent": "analytics",
            },
            "context_awareness_agent": {
                "keywords": ["context", "awareness", "activity", "focus", "focus level",
                             "active window", "running apps", "what am i doing",
                             "suggest workflow", "suggest mode", "workflow suggestion",
                             "detect workflow", "workflow patterns", "adaptive trigger",
                             "triggers", "context history", "activity summary",
                             "system load", "cpu load", "context monitoring",
                             "context rules", "context agent", "session start",
                             "session end", "my context", "current context"],
                "intent": "context",
            },
            "learning_agent": {
                "keywords": ["learn", "learning", "patterns", "habits", "recommendations",
                             "predict", "prediction", "behavior", "behavior history",
                             "analyze patterns", "learned patterns", "most common",
                             "frequent actions", "hourly pattern", "daily pattern",
                             "generate workflow", "daily routine", "morning routine",
                             "learning stats", "prediction accuracy", "suggestions",
                             "what next", "next action", "accept recommendation",
                             "dismiss recommendation", "learning agent"],
                "intent": "learning",
            },
            "communication_bus_agent": {
                "keywords": ["publish", "broadcast", "send message", "subscribe", "unsubscribe",
                             "shared state", "shared memory", "event bus", "message bus",
                             "communication bus", "comm bus", "inter-agent", "event logs",
                             "event summary", "agent activity", "communication flow",
                             "error report", "bus stats", "message status", "dlq",
                             "dead letter queue", "retry dlq", "purge dlq",
                             "registered agents", "agents on bus", "bus agents",
                             "emit event", "send event", "listen to", "remove subscription",
                             "list subscriptions", "set state", "get state", "delete state",
                             "lock state", "unlock state", "list state", "bus logs",
                             "message logs", "bus summary", "communication summary",
                             "bus errors", "communication errors", "bus statistics",
                             "check message", "delivery status", "communication bus agent"],
                "intent": "communication_bus",
            },
            "planner_agent": {
                "keywords": ["plan", "create plan", "make plan", "generate plan", "build plan",
                             "start plan", "execute plan", "run plan", "begin plan",
                             "stop plan", "halt plan", "end plan", "pause plan", "resume plan",
                             "cancel plan", "abort plan", "plan status", "check plan",
                             "plan progress", "how far along", "plan completion",
                             "list plans", "show plans", "my plans", "all plans",
                             "active plans", "current plans", "running plans",
                             "plan history", "plan log", "execution history",
                             "replan", "re-plan", "redo plan", "adjust plan", "modify plan",
                             "templates", "goal templates", "plan templates", "blueprint",
                             "add template", "new template", "create template",
                             "planner stats", "planning stats", "planner statistics",
                             "prepare for", "get ready for", "set up for", "organize for",
                             "break down", "decompose", "split into steps", "step by step",
                             "autonomous", "auto execute", "auto plan", "automate task",
                             "planner", "planner agent", "planning agent", "task planner",
                             "multi-step", "task chain", "workflow plan", "goal decomposition",
                             "dependency", "task graph", "execution chain"],
                "intent": "planner",
            },
            "marketplace_agent": {
                "keywords": ["browse", "browse marketplace", "browse agents", "browse catalog",
                             "search marketplace", "search agents", "find agent", "find agents",
                             "featured", "featured agents", "popular agents", "trending",
                             "categories", "agent categories", "browse categories",
                             "agent info", "agent details", "agent information", "view agent",
                             "install agent", "install marketplace", "get agent", "add agent",
                             "uninstall agent", "remove agent", "delete agent",
                             "update agent", "upgrade agent", "update marketplace",
                             "check updates", "check for updates", "available updates",
                             "installed", "installed agents", "my agents", "my installed",
                             "enable agent", "disable agent",
                             "review", "write review", "rate agent", "leave review",
                             "reviews", "read reviews", "agent reviews", "user reviews",
                             "verify", "verify agent", "security check", "check security",
                             "dependency tree", "show dependencies", "agent dependencies",
                             "marketplace stats", "marketplace statistics", "store stats",
                             "marketplace", "agent store", "plugin store", "app store",
                             "community agents", "download agent", "agent catalog"],
                "intent": "marketplace",
            },
        }

        best_agent = None
        best_score = 0.0
        best_intent = None

        for agent, config in agent_keywords.items():
            keywords = config["keywords"]
            intent = config["intent"]

            specific_matches = []
            for word in command_words:
                close = get_close_matches(word, keywords, n=1, cutoff=0.65)
                if close:
                    specific_matches.append(close[0])

            if specific_matches:
                score = len(specific_matches) / max(len(command_words), 1)
                if score > best_score:
                    best_score = score
                    best_agent = agent
                    best_intent = intent

        if best_agent and best_score > 0.4:
            confidence = min(0.5 + best_score * 0.4, 0.8)
            return {
                "agent": best_agent,
                "intent": best_intent or "unknown",
                "confidence": confidence,
                "params": {},
            }

        return None

    def _llm_route(self, command: str) -> Dict[str, Any]:
        """Stage 3: Use LLM to understand intent, especially with typos."""
        self.logger.info(f"LLM routing attempt for: {command}")
        prompt = (
            f"Route this user command to the correct NEXUS agent. "
            f"User command: \"{command}\"\n\n"
            f"{self._agent_descriptions}\n\n"
            f"Respond with ONLY a JSON object like this:\n"
            f'{{"agent": "agent_name", "intent": "intent_name", "confidence": 0.8}}\n\n'
            f"Agent name must be one of: file_agent, web_agent, automation_agent, coding_agent, memory_agent, vision_agent, notification_agent, scheduler_agent, knowledge_agent, terminal_agent, personality_agent, workflow_agent, plugin_agent, security_agent, workflow_chain_agent, analytics_agent, context_awareness_agent, manager. "
            f"If the command is a greeting, question, or general chat, use agent: manager, intent: conversation. "
            f"Consider typos and natural language variations."
        )

        try:
            response = self._llm.generate(prompt, system_prompt="You are a command router. Respond with valid JSON only.", temperature=0.1)
            import json
            parsed = self._parse_json_response(response)
            if parsed and parsed.get("agent") in ("file_agent", "web_agent", "automation_agent", "coding_agent", "memory_agent", "vision_agent", "notification_agent", "scheduler_agent", "knowledge_agent", "terminal_agent", "personality_agent", "workflow_agent", "plugin_agent", "security_agent", "workflow_chain_agent", "analytics_agent", "context_awareness_agent", "manager"):
                return {
                    "agent": parsed["agent"],
                    "intent": parsed.get("intent", "unknown"),
                    "confidence": min(float(parsed.get("confidence", 0.5)), 0.9),
                    "params": {"llm_corrected": True},
                }
        except Exception as e:
            self.logger.warning(f"LLM routing failed: {e}")

        return None

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        import json
        response = response.strip()

        if response.startswith("{") and response.endswith("}"):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass

        import re
        json_match = re.search(r"\{[^}]+\}", response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {}

    def _calculate_confidence(self, match, command: str) -> float:
        matched_len = match.end() - match.start()
        command_len = len(command)
        ratio = matched_len / command_len if command_len > 0 else 0
        return min(0.5 + ratio, 1.0)

    def _extract_params(self, command: str, match) -> dict:
        params = {}
        quoted = re.findall(r'"([^"]+)"', command)
        if quoted:
            params["quoted_args"] = quoted
        return params

    def add_rule(self, patterns: list, agent: str, intent: str):
        self._routing_rules.append({
            "patterns": patterns,
            "agent": agent,
            "intent": intent,
        })
        self.logger.info(f"Added routing rule: {agent}/{intent}")
