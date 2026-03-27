## Task 1A — Bare agent

**Q: What is the agentic loop?**
The agentic loop is the fundamental cycle that an autonomous AI agent follows to complete    
tasks. It typically consists of these core stages:                                           

The Loop                                                                                     

 1 Perceive — Gather information from the environment (user input, tool outputs,             
   observations)                                                                             
 2 Reason/Plan — Analyze the situation, decide what to do next, and formulate a plan         
 3 Act — Execute actions using available tools (search, file operations, API calls, etc.)    
 4 Observe — Receive feedback from the actions taken                                         
 5 Repeat — Continue the loop until the goal is achieved or a stopping condition is met      

Why It Matters                                                                               

This loop enables agents to:                                                                 

 • Work autonomously toward goals                                                            
 • Adapt based on feedback                                                                   
 • Break complex tasks into steps                                                            
 • Self-correct when things don't go as planned                                              

Example                                                                                      

For a task like "research and summarize a topic":                                            

  1 Perceive: Understand the user's request                                                  
  2 Reason: Plan to search for information, then synthesize it                               
  3 Act: Call web_search tool                                                                
  4 Observe: Read search results                                                             
  5 Reason: Determine if more info is needed                                                 
  6 Act: Fetch relevant pages with web_fetch                                                 
  7 Observe: Extract content                                                                 
  8 Reason: Synthesize findings                                                              
  9 Act: Deliver the summary to the user                                                     

This is the core pattern that powers autonomous AI agents like me! 🐈    

**Q: What labs are available in our LMS?**
I'll help you find information about available labs in your LMS. Let me first explore the    
workspace to see if there's any relevant configuration or documentation.                     

🐈 nanobot
I can see there's a lab directory and an instructors directory. Let me explore these to find 
information about available labs.                                                            

🐈 nanobot
Based on the repository structure, here are the available labs in your LMS (Lab 8 — "The     
Agent is the Interface"):                                                                    

Required Tasks                                                                               

 1 Task 1: Set Up the Agent                                                                  
    • Install nanobot                                                                        
    • Configure Qwen API                                                                     
    • Add MCP tools                                                                          
    • Write skill prompt                                                                     
 2 Task 2: Deploy and Connect a Web Client                                                   
    • Dockerize nanobot                                                                      
    • Add WebSocket channel + Flutter chat UI                                                
 3 Task 3: Give the Agent New Eyes                                                           
    • Explore observability data                                                             
    • Write log/trace MCP tools                                                              
 4 Task 4: Diagnose a Failure and Make the Agent Proactive                                   
    • Investigate a failure                                                                  
    • Schedule in-chat health checks                                                         
    • Fix a planted bug                                                                      
 5 Task 5 (details in file)                                                                  

Optional Tasks                                                                               

 1 Task 1: Add a Telegram Bot Client                                                         
    • Same agent, different interface                                                        

What You'll Build                                                                            

The lab focuses on creating an AI agent interface for an LMS (Learning Management System)    
that:                                                                                        

 • Answers questions in natural language ("which lab has the lowest pass rate?")             
 • Queries the LMS backend via MCP tools                                                     
 • Monitors system health using observability tools (logs/traces)                            
 • Can be accessed via web chat or Telegram                                                  

Would you like me to read the details of any specific task?  
## Task 1B — Agent with LMS tools
**Q: What labs are available?**
Great! The LMS now has 8 labs available:                                                     

                                                             
 ID  Lab Title                                               
 ─────────────────────────────────────────────────────────── 
 1   Lab 01 – Products, Architecture & Roles                 
 2   Lab 02 — Run, Fix, and Deploy a Backend Service         
 3   Lab 03 — Backend API: Explore, Debug, Implement, Deploy 
 4   Lab 04 — Testing, Front-end, and AI Agents              
 5   Lab 05 — Data Pipeline and Analytics Dashboard          
 6   Lab 06 — Build Your Own Agent                           
 7   Lab 07 — Build a Client with an AI Coding Agent         
 8   lab-08 (The Agent is the Interface)                     
                                                             

You're currently working on Lab 08, which focuses on building an AI agent interface for the  
LMS using nanobot.                                                                           

Would you like me to check pass rates, completion stats, or learner data for any specific    
lab?                        

**Q: Describe the architecture of the LMS system**
                                 🏗️ LMS System Architecture                                  

The Learning Management Service (LMS) is a multi-container application built with modern     
cloud-native technologies. Here's the complete architecture:                                 

---------------------------------------------------------------------------------------------

📦 Core Components                                                                           

1. Backend (FastAPI)                                                                         

 • Framework: Python FastAPI                                                                 
 • Port: 8000 (container), exposed on host port 42001                                        
 • Responsibilities:                                                                         
    • REST API for items (labs/tasks), learners, and interactions                            
    • ETL pipeline to sync data from external autochecker API                                
    • Analytics endpoints                                                                    
    • OpenTelemetry instrumentation (traces + logs)                                          
 • API Key Authentication: All endpoints protected by LMS_API_KEY                            

2. Database (PostgreSQL 18.3)                                                                

 • Port: 5432 (container), exposed on host port 42004                                        
 • Schema:                                                                                   
    • item — labs and tasks (tree structure with parent_id)                                  
    • learner — students (anonymized external IDs)                                           
    • interacts — submission records with scores                                             
 • Initialization: init.sql runs on first start                                              

3. Database Admin (pgAdmin)                                                                  

 • Port: 80 (container), exposed on host port 42003                                          
 • Access: admin@example.com / admin                                                         
 • Restricted: Only accessible from localhost/private networks                               

4. Reverse Proxy (Caddy)                                                                     

 • Port: 80 (container), exposed on host port 42002                                          
 • Routes:                                                                                   
    • /items*, /learners*, /interactions*, /pipeline*, /analytics* → Backend                 
    • /docs*, /openapi.json → Swagger UI                                                     
    • /utils/pgadmin* → pgAdmin (restricted)                                                 
    • /utils/victorialogs* → VictoriaLogs (restricted)                                       
    • /utils/victoriatraces* → VictoriaTraces (restricted)                                   
    • / → React SPA (fallback)                                                               
 • Security: Admin tools blocked from public IPs                                             

5. LLM Gateway (Qwen Code API)                                                               

 • Port: 8080 (container), exposed  
## Task 1C - Skill prompt
Here are the complete average scores for all 8 labs:                                         

📊 Lab Scores Summary                                                                        

Lab 01 – Products, Architecture & Roles                                                      

                                                                 
 Task                                        Avg Score  Attempts 
 ─────────────────────────────────────────────────────────────── 
 Lab setup                                   84.3%      3080     
 Task 0: Practice the Git workflow           64.5%      306      
 Task 1: Product & architecture description  55.1%      161      
 Task 2: Roles and skills mapping            49.8%      83       
 Optional: Resolve a merge conflict          34.6%      13       
 Optional: Add a CI check                    42.9%      7        
 Optional: Create a release                  60.0%      5        
 Optional: Plan skill development            20.0%      5        
                                                                 

Lab 02 — Run, Fix, and Deploy a Backend Service                                              

                                                                     
 Task                                            Avg Score  Attempts 
 ─────────────────────────────────────────────────────────────────── 
 Task 1: Run the web server                      67.9%      210      
 Task 2: Identify, report, and fix a bug         66.7%      216      
 Task 4: Deploy the web server to the VM         56.2%      84       
 Optional 3: Implement the post-order traversal  62.5%      6        
 Optional 1: Implement the /outcomes endpoint    36.4%      11       
 Optional 2: Make your VM a proxy                0.0%       3        
                                                                     

Lab 03 — Backend API: Explore, Debug, Implement, Deploy                                      

                                                                         
 Task                                                Avg Score  Attempts 
 ─────────────────────────────────────────────────────────────────────── 
 Task 1: Explore the API                             63.7%      381      
 Task 2: Enable and debug the interactions endpoint  66.4%      299      
 Task 3: Implement the learners endpoint             50.0%      4        
 Task 4: Deploy to a hardened VM              
