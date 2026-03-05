# AI Model Manager

A modern AI model management and optimization skill for OpenClaw that provides intelligent model selection, performance monitoring, and cost optimization capabilities.

## Features

### 🤖 Smart Model Selection
- **Task Complexity Analysis**: Automatically determine optimal models based on task requirements
- **Performance-Based Selection**: Choose models that balance speed, quality, and cost
- **Context-Aware Switching**: Maintain conversation continuity during model changes
- **Learning Patterns**: Improve recommendations based on historical performance

### 📊 Performance Monitoring
- **Real-time Metrics**: Track response times, token usage, and quality scores
- **Historical Analysis**: Analyze usage trends and performance patterns
- **Model Comparison**: Compare performance across different models
- **Quality Scoring**: Evaluate model output quality based on task completion

### 💰 Cost Optimization
- **Intelligent Cost Control**: Automatically select cost-effective models
- **Budget Management**: Track daily/weekly/monthly usage and set limits
- **Cost Analysis**: Generate detailed cost breakdowns and optimization reports
- **ROI Analysis**: Calculate return on investment for different model tiers

### ⚙️ Configuration Management
- **Task-Specific Settings**: Configure optimal models for different task types
- **Strategy Profiles**: Pre-configured strategies for different use cases
- **Import/Export**: Save and share configurations across environments
- **Auto-Configuration**: Automatically configure based on usage patterns

## Installation

The AI Model Manager skill is automatically available when OpenClaw is properly installed:

```bash
# Verify the skill is recognized
openclaw skills list | grep ai-model-manager

# Run the demo
cd ~/oepnclaw/openclaw-main/skills/ai-model-manager
./example.sh
```

## Quick Start

### Basic Usage

```bash
# Check current model
ai-model-manager current

# List available models
ai-model-manager models

# Get model recommendations
ai-model-manager recommend --prompt "Write a Python script for data analysis"
```

### Performance Monitoring

```bash
# Monitor current session
ai-model-manager monitor --current

# Historical performance analysis
ai-model-manager history --days 7

# Model comparison
ai-model-manager compare --models zai/glm-5,zai/glm-4.7,zai/glm-4.5-air
```

### Cost Optimization

```bash
# Current session costs
ai-model-manager cost --current

# Usage statistics
ai-model-manager usage --period daily

# Cost optimization report
ai-model-manager optimize --target performance
```

### Configuration

```bash
# Set task-specific models
ai-model-manager config --task coding --model zai/glm-5
ai-model-manager config --task analysis --model zai/glm-4.7
ai-model-manager config --task documentation --model zai/glm-4.5-air

# Apply pre-configured strategies
ai-model-manager apply --strategy developer-workflow
ai-model-manager apply --strategy cost-conscious
ai-model-manager apply --strategy performance-mode
```

## Advanced Usage

### Smart Selection Modes

```bash
# Automatic model selection based on complexity
ai-model-manager switch --task-type complex

# Performance optimization
ai-model-manager optimize --metric quality --budget-aware

# Cost-performance analysis
ai-model-manager efficiency --model zai/glm-5 --task-type analysis
```

### Configuration Templates

```bash
# Developer workflow configuration
ai-model-manager template apply --name developer --auto

# Custom configuration creation
ai-model-manager template create --name my-workflow \
  --task coding --model zai/glm-5 \
  --task analysis --model zai/glm-4.7 \
  --task documentation --model zai/glm-4.5-air

# Export configuration
ai-model-manager export --file my-config.json
```

### Integration with External Tools

```bash
# Research current model capabilities
ai-model-manager research --topic "latest AI model performance"

# Compare with external benchmarks
ai-model-manager benchmark --provider openai --model gpt-4

# Generate reports
ai-model-manager report --format pdf --output cost-report.pdf
```

## Configuration Templates

### Developer Workflow
```bash
ai-model-manager apply --template developer-workflow
```
- Coding tasks: zai/glm-5 (maximum performance)
- Debugging: zai/glm-4.7 (balanced)
- Documentation: zai/glm-4.5-air (cost-effective)
- Analysis: zai/glm-5 (detailed insights)

### Cost-Conscious Mode
```bash
ai-model-manager apply --template cost-conscious
```
- Daily budget: $25
- Cost optimization: Priority
- Model selection: Most cost-effective for task type
- Quality threshold: Minimum acceptable level

### Performance Mode
```bash
ai-model-manager apply --template performance-mode
```
- Performance priority: Maximum
- Cost consideration: Secondary
- Model selection: Highest capability available
- Quality: Maximum achievable

## Monitoring and Analytics

### Real-time Monitoring
```bash
# Current session metrics
ai-model-manager monitor --current --detailed

# Performance alerts
ai-model-manager alert --threshold response-time 5s

# Cost warnings
ai-model-manager alert --threshold daily-cost 20
```

### Historical Analysis
```bash
# Usage trends
ai-model-manager trends --metric response-time --period week

# Performance comparison
ai-model-manager compare --period week --metric quality

# Cost analysis
ai-model-manager cost-analysis --period month --trend
```

## API and Automation

### Command Line Interface
```bash
# All commands accept JSON output for automation
ai-model-manager current --format json
ai-model-manager models --format json
ai-model-manager cost --format json --period session
```

### Script Integration
```bash
#!/bin/bash
# Example script for automated model management

# Check current performance
CURRENT_PERFORMANCE=$(ai-model-manager monitor --current --metric response-time)

# Switch to optimal model if needed
if (( $(echo "$CURRENT_PERFORMANCE > 3.0" | bc -l) )); then
    ai-model-manager switch --model zai/glm-5
fi

# Check costs
ai-model-manager cost --current --format json
```

## Performance Optimization

### Model Selection Strategy
```bash
# Balance performance and cost
ai-model-manager optimize --balance performance-cost --weight 0.7

# Prioritize speed
ai-model-manager optimize --priority speed --model zai/glm-4.5-air

# Maximum quality
ai-model-manager optimize --priority quality --model zai/glm-5
```

### Resource Management
```bash
# Memory optimization
ai-model-manager optimize --memory --limit 4gb

# CPU optimization
ai-model-manager optimize --cpu --threads 4

# Network optimization
ai-model-manager optimize --network --cache true
```

## Troubleshooting

### Common Issues

**Model Not Available**
```bash
# Check model availability
ai-model-manager models validate --model zai/glm-5

# List available models
ai-model-manager models list --available
```

**Cost Tracking Errors**
```bash
# Reset cost tracking
ai-model-manager reset --cost

# Verify token counting
ai-model-manager verify --tokens
```

**Performance Issues**
```bash
# Check system performance
ai-model-manager system --check

# Monitor resource usage
ai-model-manager monitor --resources
```

### Debug Commands
```bash
# Enable debug mode
ai-model-manager debug --on

# View logs
ai-model-manager logs --level debug

# Test model switching
ai-model-manager test --model zai/glm-5 --prompt "Test prompt"
```

## Best Practices

### For Developers
1. **Profile Your Workload**: Analyze your typical task types and complexity
2. **Set Realistic Budgets**: Configure cost limits appropriate for your usage
3. **Monitor Performance**: Regularly check response times and quality metrics
4. **Test Model Changes**: Validate model switches on non-critical tasks first

### For Cost Optimization
1. **Use Tiered Models**: Select appropriate models for different task complexities
2. **Monitor Usage**: Track daily costs and adjust strategies accordingly
3. **Set Limits**: Implement budget limits to prevent unexpected costs
4. **Review Periodically**: Analyze cost patterns and optimize regularly

### For Performance
1. **Balance Quality and Speed**: Consider both factors when selecting models
2. **Monitor Response Times**: Track and optimize for performance
3. **Use Caching**: Enable caching where appropriate to improve speed
4. **Profile Workloads**: Understand your performance requirements

## Contributing

To contribute improvements to the AI Model Manager skill:

1. Review the SKILL.md documentation
2. Test new features thoroughly
3. Update examples and documentation
4. Follow the existing code style and patterns
5. Submit pull requests with detailed descriptions

## Support

For issues or questions:
- Check the troubleshooting section
- Review the example.sh script
- Consult the OpenClaw documentation
- Create an issue in the OpenClaw repository

---

*This skill is designed to work with OpenClaw's model management system and requires proper configuration to function optimally.*