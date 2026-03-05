---
name: ai-model-manager
description: "Modern AI model management and optimization for OpenClaw. Use for model switching, performance monitoring, cost tracking, and configuration management. NOT for: model training, fine-tuning, or complex pipeline orchestration."
homepage: https://docs.openclaw.ai/skills/ai-model-manager
metadata: { "openclaw": { "emoji": "🤖", "requires": { "tools": ["openclaw", "web_search"], "anyBins": ["curl"] } } }
---

# AI Model Manager

Modern AI model management and optimization for OpenClaw deployments. Provides model switching, performance monitoring, cost tracking, and intelligent model selection based on task complexity.

## When to Use

✅ **USE this skill when:**

- "Switch to a more powerful model for complex tasks"
- "Check model performance and usage statistics"
- "Optimize costs by selecting appropriate models"
- "Monitor model usage patterns"
- "Configure model preferences for different task types"
- "Compare model capabilities and response quality"

## When NOT to Use

❌ **DON'T use this skill when:**

- Model training or fine-tuning → use specialized ML frameworks
- Complex pipeline orchestration → use workflow automation tools
- Custom model development → use development environments
- Large-scale model deployment → use MLOps tools
- Real-time model serving → use serving infrastructure

## Core Features

### Model Intelligence

**Smart Model Selection**
- Analyze task complexity and suggest optimal models
- Balance performance vs. cost based on usage patterns
- Learn from past performance to improve recommendations

**Context-Aware Switching**
- Switch models based on task requirements
- Maintain session continuity during model changes
- Preserve conversation context when switching models

### Performance Monitoring

**Real-time Metrics**
- Response time tracking
- Token usage analysis
- Quality scoring based on task completion
- Error rate monitoring

**Historical Analysis**
- Usage trends over time
- Performance comparison across models
- Cost optimization insights
- Quality improvement patterns

### Cost Optimization

**Intelligent Cost Control**
- Automatic model selection based on budget constraints
- Cost alerts and recommendations
- Usage-based model downgrading
- Task complexity analysis for cost allocation

**Budget Management**
- Daily/weekly/monthly cost tracking
- Predictive cost modeling
- Spending alerts and limits
- ROI analysis for different model tiers

## Commands

### Model Management

```bash
# List available models with details
openclaw models list --verbose

# Show current model configuration
openclaw models current

# Switch to specific model
openclaw models switch --model zai/glm-5

# Switch model based on complexity
ai-model-manager switch --task-type complex

# Get model recommendations
ai-model-manager recommend --prompt "Write a detailed technical analysis"
```

### Performance Monitoring

```bash
# Monitor current session performance
ai-model-manager monitor --current

# Historical performance analysis
ai-model-manager history --days 7

# Model comparison report
ai-model-manager compare --models zai/glm-5,zai/glm-4.5-air

# Performance trends
ai-model-manager trends --metric response-time
```

### Cost Tracking

```bash
# Current session cost
ai-model-manager cost --current

# Usage statistics
ai-model-manager usage --period daily

# Cost optimization report
ai-model-manager optimize --target performance

# Budget status
ai-model-manager budget --current --limit 50
```

### Configuration

```bash
# Auto-configuration based on usage patterns
ai-model-manager auto-config

# Set task-specific models
ai-model-manager config --task coding --model zai/glm-5
ai-model-manager config --task analysis --model zai/glm-4.7

# Export configuration
ai-model-manager export --file model-config.json

# Import configuration
ai-model-manager import --file model-config.json
```

## Smart Selection Modes

### Task Complexity Analysis

```bash
# Automatic model selection based on prompt complexity
ai-model-manager analyze --prompt "Your task here"

# Complexity scoring
ai-model-manager complexity --score --prompt "Simple question"

# Model recommendation with confidence
ai-model-manager recommend --prompt "Complex technical analysis" --confidence
```

### Performance-Based Optimization

```bash
# Find optimal model for current workload
ai-model-manager optimize --metric quality

# Balance speed vs. quality
ai-model-manager balance --speed-weight 0.7 --quality-weight 0.3

# Cost-performance analysis
ai-model-manager efficiency --model zai/glm-5 --task-type analysis
```

## Quick Responses

**"Switch to a better model for complex task"**

```bash
ai-model-manager switch --task-type complex
openclaw models switch --model zai/glm-5
```

**"Check how much this session is costing"**

```bash
ai-model-manager cost --current
ai-model-manager usage --period session
```

**"Optimize for performance vs. cost"**

```bash
ai-model-manager optimize --target performance --budget-aware
```

**"Get model recommendations for my task"**

```bash
ai-model-manager recommend --prompt "Your task description here" --confidence
```

## Configuration Templates

### Developer Workflow

```bash
# Optimize for coding tasks
ai-model-manager config --task coding --model zai/glm-5
ai-model-manager config --task debugging --model zai/glm-4.7
ai-model-manager config --task documentation --model zai/glm-4.5-air
```

### Cost-Conscious Mode

```bash
# Set cost optimization preferences
ai-model-manager config --strategy cost-first --limit 25
ai-model-manager config --task analysis --model zai/glm-4.5-air
ai-model-manager config --task creative --model zai/glm-4.7
```

### Performance Mode

```bash
# Prioritize performance over cost
ai-model-manager config --strategy performance-first
ai-model-manager config --task complex --model zai/glm-5
ai-model-manager config --task research --model zai/glm-5
```

## Advanced Features

### Adaptive Learning

**Usage Pattern Analysis**
- Track task types and their model performance
- Learn optimal model selection patterns
- Predict best model for new task types

**Continuous Improvement**
- Update recommendations based on historical performance
- Adapt to changing usage patterns
- Model performance degradation detection

### Integration with External Tools

**Web Search Integration**
```bash
# Research current model capabilities
ai-model-manager research --topic "latest AI model performance"

# Compare with external benchmarks
ai-model-manager benchmark --provider openai --model gpt-4
```

**Cost Tracking Integration**
```bash
# Link with billing systems
ai-model-manager integrate --service billing --api-key $API_KEY

# Generate cost reports
ai-model-manager report --format pdf --output cost-report.pdf
```

## Notes

- Requires OpenClaw models to be properly configured
- Works best with multiple model tiers available
- Learning improves with usage over time
- Configuration changes take effect immediately
- Cost tracking accuracy depends on token counting precision

## Safety Guidelines

- **Cost Awareness**: Always consider budget impact when switching models
- **Performance Balance**: Don't sacrifice essential quality for cost savings
- **Testing**: Test model changes on non-critical tasks first
- **Monitoring**: Monitor performance after model switches
- **Documentation**: Keep track of model changes and their outcomes

## Troubleshooting

**Common Issues**
- Model switching failures: Check model availability and permissions
- Cost tracking errors: Verify token counting configuration
- Performance monitoring: Ensure session tracking is enabled
- Configuration conflicts: Review existing task-model mappings

**Debug Commands**
```bash
# Check model availability
openclaw models validate --model zai/glm-5

# Reset configuration
ai-model-manager reset --config

# Clear usage history
ai-model-manager clear --history

# Test model switching
ai-model-manager test --model zai/glm-5 --prompt "Test prompt"
```