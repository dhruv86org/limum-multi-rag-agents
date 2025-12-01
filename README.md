# Multi-Agent RAG Orchestration System

A production-grade multi-agent system that intelligently routes user queries to specialized RAG (Retrieval-Augmented Generation) agents, with complete workflow tracing via Langfuse.

## 🎯 Overview

This system solves the real-world problem of handling diverse queries with domain-specific knowledge by:

1. **Classifying** user intent using an intelligent orchestrator
2. **Routing** queries to specialized RAG agents (HR, Tech, Finance)
3. **Grounding** answers in company documentation to prevent hallucinations
4. **Tracing** complete execution paths with Langfuse for debugging and monitoring
5. **Evaluating** response quality with automated scoring

## 🏗️ Architecture

```
User Query → Orchestrator (LLM-based Intent Classification)
                    ↓
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    HR Agent    Tech Agent  Finance Agent
    (RAG)       (RAG)       (RAG)
        ↓           ↓           ↓
   HR Vector   Tech Vector Finance Vector
    Store        Store       Store
    (FAISS)      (FAISS)     (FAISS)
```

### Components

- **Orchestrator**: LLM-based query classifier that routes to appropriate agent
- **Specialized RAG Agents**: Domain-specific agents with dedicated knowledge bases
  - **HR Agent**: Employee policies, benefits, leave policies, onboarding
  - **Tech Agent**: API documentation, deployment guides, security standards
  - **Finance Agent**: Expense policies, budgets, procurement procedures
- **Vector Stores**: FAISS indexes for efficient semantic search (50+ chunks per domain)
- **Langfuse Integration**: Complete observability with execution tracing
- **Evaluator Agent**: Automated quality scoring on relevance, completeness, accuracy, clarity

## 📋 Prerequisites

- Python 3.10+
- OpenRouter API key (for OpenAI models)
- Langfuse account and API keys

## 🚀 Quick Start

### 1. Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd workspace

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY: Your OpenRouter API key
# - OPENAI_API_BASE: https://openrouter.ai/api/v1
# - LANGFUSE_PUBLIC_KEY: Your Langfuse public key
# - LANGFUSE_SECRET_KEY: Your Langfuse secret key
# - LANGFUSE_HOST: https://cloud.langfuse.com
```

### 3. Run the Notebook

```bash
# Start Jupyter
jupyter notebook

# Open multi_agent_system.ipynb
# Run cells in order to:
# 1. Load and chunk documents
# 2. Create vector stores
# 3. Initialize agents
# 4. Test the system
```

### 4. Execute in Order

The notebook is designed to be run sequentially:

1. **Setup & Imports** - Load libraries and configure environment
2. **Document Loading** - Create vector stores from markdown docs
3. **Agent Definitions** - Initialize specialized RAG agents
4. **Orchestrator & Routing** - Set up intent classification
5. **Testing & Examples** - Run sample queries
6. **Langfuse Integration** - View traces and analytics
7. **Evaluator Agent** - Automated quality scoring
8. **Batch Testing** - Run comprehensive test suite

## 📁 Project Structure

```
workspace/
├── multi_agent_system.ipynb  # Main notebook implementation
├── test_queries.json          # Test queries with expected categories
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── README.md                  # This file
├── data/                      # Document collections
│   ├── hr_docs/               # HR knowledge base (50+ chunks)
│   │   ├── employee_handbook.md
│   │   ├── onboarding_guide.md
│   │   └── leave_policies.md
│   ├── tech_docs/             # Technical knowledge base (50+ chunks)
│   │   ├── api_documentation.md
│   │   ├── deployment_guide.md
│   │   └── security_standards.md
│   └── finance_docs/          # Finance knowledge base (50+ chunks)
│       ├── expense_policy.md
│       ├── budget_guidelines.md
│       └── procurement_policy.md
└── vector_stores/             # Generated FAISS indexes (created on first run)
    ├── hr_vector_store/
    ├── tech_vector_store/
    └── finance_vector_store/
```

## 🎯 Usage Examples

### Basic Query

```python
from multi_agent_system import route_query, display_response

# Ask a question
response = route_query("How much PTO do I get after 3 years?")
display_response(response)

# Output:
# Classification: HR
# Routing to HR Agent...
# Answer: After 3 years of employment at TechCorp, you receive 20 days 
# (160 hours) of PTO per year...
```

### With Evaluation

```python
from multi_agent_system import evaluate_response, display_evaluation

# Get response and evaluate
response = route_query("What is the API rate limit?")
scores = evaluate_response(response)
display_evaluation(scores)

# Output:
# Relevance: 5.0/5
# Completeness: 4.5/5
# Accuracy: 5.0/5
# Clarity: 5.0/5
# Overall Score: 4.9/5
```

### Batch Testing

```python
from multi_agent_system import run_batch_tests

queries = [
    "How do I submit an expense report?",
    "What are the webhook events in the API?",
    "Can I work remotely?"
]

results = run_batch_tests(queries, evaluate=True)
# Automatically routes, evaluates, and summarizes all queries
```

## 🧪 Testing

### Test Queries

The project includes 23 test queries in `test_queries.json`:
- 7 HR queries (PTO, benefits, onboarding, remote work)
- 7 Tech queries (API, deployment, security)
- 6 Finance queries (expenses, budgets, procurement)
- 3 Edge cases (greetings, out-of-scope, invalid)

### Running Tests

```python
import json

# Load test queries
with open('test_queries.json') as f:
    test_data = json.load(f)

# Run all test queries
queries = [q['query'] for q in test_data['test_queries']]
results = run_batch_tests(queries, evaluate=True)

# View summary statistics
# - Routing accuracy
# - Average quality scores
# - Performance metrics
```

## 📊 Langfuse Tracing

All queries are automatically traced in Langfuse for complete observability.

### What Gets Traced

- Intent classification decisions
- Agent selection logic
- Vector store retrieval (documents found)
- LLM prompt and response
- Token usage and costs
- Execution timeline
- Quality evaluation scores

### Accessing Traces

1. Log into https://cloud.langfuse.com
2. Navigate to your project
3. View traces in the "Traces" tab
4. Filter by:
   - Category (HR, Tech, Finance)
   - Quality scores
   - Token usage
   - Time range

### Example Trace Analysis

```python
# Traces show:
# 1. Orchestrator classified query as "TECH"
# 2. Tech agent retrieved 5 documents
# 3. Documents about API authentication
# 4. LLM generated response (234 tokens)
# 5. Evaluator scored 4.8/5
# 6. Total latency: 1.2s
```

## 🏆 Technical Decisions

### Why LangChain?

**Chosen for production-grade components:**
- ✅ `RetrievalQA`: Battle-tested RAG implementation
- ✅ `FAISS`: Efficient vector search
- ✅ `PromptTemplate`: Structured prompt management
- ✅ Community support and active development
- ✅ Easy to extend with new agents or retrieval strategies

**Alternative considered**: Custom RAG implementation
- ❌ Requires maintaining fragile custom code
- ❌ Lacks standardization and best practices
- ❌ Harder to debug and iterate

### Why Separate Vector Stores?

**Chosen for domain isolation:**
- ✅ More focused retrieval per domain
- ✅ Can update one domain without affecting others
- ✅ Better relevance (smaller search space)
- ✅ Scalable to add new domains

**Alternative considered**: Single unified vector store
- ❌ Retrieval less focused (searches all domains)
- ❌ Harder to maintain domain boundaries
- ❌ Risk of cross-domain contamination

### Why LLM-Based Orchestrator?

**Chosen for intelligent routing:**
- ✅ Handles complex, multi-domain queries
- ✅ More robust than keyword matching
- ✅ Can explain routing decisions (Langfuse)
- ✅ Adapts to query variations naturally

**Alternative considered**: Keyword/rule-based routing
- ❌ Brittle with edge cases
- ❌ Requires maintaining keyword lists
- ❌ Poor handling of ambiguous queries

### Why Langfuse for Tracing?

**Chosen for production monitoring:**
- ✅ Complete execution visibility
- ✅ Built-in LangChain integration
- ✅ Quality metrics over time
- ✅ Easy debugging of failures
- ✅ Cost tracking and optimization

**Alternative considered**: Custom logging
- ❌ Requires building analytics dashboard
- ❌ No automatic LLM call tracking
- ❌ Limited query/debugging interface

## 🔧 Configuration

### Model Configuration

Edit `.env` to customize models:

```bash
# LLM for agents and orchestrator
OPENAI_MODEL=openai/gpt-4-turbo-preview

# Embedding model for vector stores
EMBEDDING_MODEL=openai/text-embedding-ada-002
```

### Retrieval Configuration

Edit `CONFIG` in notebook:

```python
CONFIG = {
    'chunk_size': 1000,        # Document chunk size
    'chunk_overlap': 200,      # Overlap between chunks
    'retrieval_k': 5,          # Documents to retrieve per query
    'temperature': 0.1,        # LLM temperature (low for consistency)
}
```

### Agent Customization

To add a new agent:

1. Create document collection in `data/new_domain_docs/`
2. Load documents and create vector store
3. Define agent prompt template
4. Create RAG agent with `create_rag_agent()`
5. Update orchestrator categories
6. Add to routing logic

## 📈 Quality Evaluation

### Evaluation Dimensions

Each response is scored on:

1. **Relevance (1-5)**: Does it answer the question?
2. **Completeness (1-5)**: Is all necessary info included?
3. **Accuracy (1-5)**: Is information correct per sources?
4. **Clarity (1-5)**: Is it well-structured and understandable?

### Interpreting Scores

- **5.0**: Exceptional - production quality
- **4.0-4.9**: Good - minor improvements possible
- **3.0-3.9**: Acceptable - review for improvements
- **< 3.0**: Poor - needs attention

### Continuous Monitoring

Scores are sent to Langfuse for:
- Tracking quality over time
- Identifying low-quality responses
- A/B testing prompt changes
- Detecting degradation

## 🚨 Troubleshooting

### "Missing environment variables"

**Problem**: `.env` file not configured

**Solution**:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### "No module named 'langchain'"

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

### "Rate limit exceeded"

**Problem**: Too many API calls

**Solution**:
- Wait for rate limit reset
- Upgrade OpenRouter plan
- Reduce batch test size

### "Vector store not found"

**Problem**: Vector stores not created

**Solution**:
```python
# Re-run section 2 of notebook to create vector stores
```

### Poor retrieval results

**Problem**: Documents not well-chunked or embedded

**Solution**:
- Adjust `chunk_size` and `chunk_overlap`
- Increase `retrieval_k` for more context
- Review document quality and formatting

## 🔐 Security Considerations

### API Keys
- ✅ Never commit `.env` to version control
- ✅ Use environment variables for all secrets
- ✅ Rotate keys periodically
- ✅ Use separate keys for dev/staging/prod

### Data Privacy
- ✅ Document collections contain no PII
- ✅ All queries traced in Langfuse (review data retention policy)
- ✅ Vector stores stored locally (not in cloud by default)

## 📚 Dependencies

Core libraries:
- `langchain` - RAG framework
- `langchain-openai` - OpenAI integration
- `langfuse` - Tracing and observability
- `faiss-cpu` - Vector similarity search
- `openai` - OpenAI API client
- `python-dotenv` - Environment management

See `requirements.txt` for complete list with versions.

## 🎓 Learning Resources

### LangChain
- [LangChain Documentation](https://python.langchain.com/)
- [RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [RetrievalQA Guide](https://python.langchain.com/docs/modules/chains/popular/vector_db_qa)

### Langfuse
- [Langfuse Documentation](https://langfuse.com/docs)
- [LangChain Integration](https://langfuse.com/docs/integrations/langchain)
- [Evaluation Guide](https://langfuse.com/docs/scores/overview)

### RAG Systems
- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [Best Practices](https://www.anthropic.com/index/retrieval-augmented-generation)

## 🤝 Contributing

To extend this system:

1. **Add new documents**: Place in `data/<domain>_docs/`
2. **Create new agent**: Follow pattern in section 3
3. **Update orchestrator**: Add category to classification
4. **Add tests**: Update `test_queries.json`
5. **Document changes**: Update this README

## 📝 Known Limitations

1. **Single-domain routing**: Each query routed to one agent
   - Multi-domain queries may need multiple agents
   - Consider implementing agent collaboration

2. **Static retrieval**: Fixed number of documents retrieved
   - Could implement dynamic retrieval based on query complexity
   - Consider re-ranking retrieved documents

3. **No conversation memory**: Each query independent
   - Could add conversation history for follow-ups
   - Implement session management

4. **English only**: Documents and queries in English
   - Could add multi-language support
   - Separate vector stores per language

## 🔮 Future Enhancements

- [ ] Multi-agent collaboration for complex queries
- [ ] Conversation memory and session management
- [ ] Hybrid search (vector + keyword)
- [ ] Document re-ranking
- [ ] Real-time document updates
- [ ] Web UI for easier interaction
- [ ] Multi-language support
- [ ] Custom embedding fine-tuning
- [ ] A/B testing framework for prompts

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Check Langfuse docs: https://langfuse.com/docs
- Review LangChain docs: https://python.langchain.com/

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) for RAG framework
- [Langfuse](https://langfuse.com/) for tracing and observability
- [OpenRouter](https://openrouter.ai/) for LLM access
- [FAISS](https://github.com/facebookresearch/faiss) for vector search

---

**Built for production use with real-world company documentation.**

Last updated: January 2025
