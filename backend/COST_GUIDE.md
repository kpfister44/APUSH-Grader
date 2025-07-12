# APUSH Grader - Cost Guide for Teachers

## Overview
This guide helps teachers understand the costs and usage limits for using APUSH Grader with real AI grading.

## Cost Breakdown

### **Anthropic AI Costs**
- **Cost per essay**: ~$0.02-0.03 (2-3 cents)
- **100 essays**: ~$2-3 per day
- **Monthly estimate** (2,000 essays): ~$40-60

### **Hosting Costs**
- **Railway hosting**: $5-10/month
- **Total monthly cost**: $45-70 for moderate usage

## Built-in Cost Protection

### **Daily Limits (Automatic)**
- ✅ **100 essays per day maximum**
- ✅ **50,000 words per day maximum** 
- ✅ **20 requests per minute maximum**
- ✅ **50 essays per hour maximum**

### **What Happens When Limits Are Reached**
- System shows friendly error message
- No additional charges incurred
- Limits reset automatically at midnight
- Teachers can track usage via health dashboard

## Typical Teacher Usage Scenarios

### **Light Usage Teacher**
- **10-20 essays per day**
- **Monthly cost**: ~$15-25
- **Perfect for**: Individual classroom use, occasional grading

### **Moderate Usage Teacher**
- **30-50 essays per day**
- **Monthly cost**: ~$25-40
- **Perfect for**: Multiple classes, regular AP practice

### **Heavy Usage Teacher**
- **70-100 essays per day (hitting daily limit)**
- **Monthly cost**: ~$50-70
- **Perfect for**: Multiple AP classes, department head, shared usage

### **Department Usage**
- **2-12 teachers sharing one system**
- **Monthly cost**: ~$60-120 depending on usage
- **Perfect for**: School department, cost-effective shared resource

## Cost Comparison

### **Traditional Grading**
- **Teacher time**: 10-15 minutes per essay
- **100 essays**: 16-25 hours of teacher time
- **Hourly rate**: Teacher's time value

### **APUSH Grader**
- **AI grading**: ~30 seconds per essay
- **Teacher review**: 2-3 minutes per essay
- **100 essays**: ~3-5 hours total time + $2-3 cost
- **Time savings**: 12-20 hours per 100 essays

## Setting Up Cost Controls

### **Anthropic Console Settings**
1. Visit [console.anthropic.com](https://console.anthropic.com/)
2. Go to "Usage" → "Settings"
3. Set monthly spending limit (recommended: $50-100)
4. Set up email alerts at 50% and 80% usage
5. Configure automatic suspension at 100% limit

### **Recommended Monthly Limits**
- **Individual teacher**: $50/month
- **Small department (2-3 teachers)**: $100/month
- **Large department (4+ teachers)**: $150/month

## Monitoring Usage

### **Real-Time Monitoring**
- Visit: `http://your-domain.com/usage/summary`
- Shows: Daily essay count, word count, remaining limits
- Updates: Real-time usage tracking

### **Daily Usage Example**
```json
{
  "date": "2024-01-15",
  "essays_graded": 45,
  "total_words": 22500,
  "estimated_cost": "$1.35",
  "limits": {
    "essays_remaining": 55,
    "words_remaining": 27500
  }
}
```

## Budget Planning

### **Monthly Budget Calculator**
- **Expected essays per day**: _____ essays
- **Days per month**: ~20 school days
- **Monthly essays**: _____ × 20 = _____ essays
- **Estimated cost**: _____ essays × $0.025 = $_____ AI costs
- **Hosting cost**: $8/month
- **Total budget**: $_____ + $8 = $_____

### **Cost-Saving Tips**
1. **Use mock mode for practice** - No AI costs during teacher training
2. **Batch grading sessions** - More efficient than scattered usage
3. **Share between teachers** - Split costs across department
4. **Set conservative daily limits** - Prevent unexpected overages
5. **Monitor usage weekly** - Stay aware of spending patterns

## Budget Approval Template

### **For School Administration**
```
APUSH Grader Budget Request

Purpose: AI-powered essay grading to reduce teacher workload and improve feedback quality

Benefits:
- Saves 12-20 hours per 100 essays graded
- Provides consistent, detailed feedback to students
- Allows teachers to focus on instruction rather than grading
- Supports AP exam preparation with College Board rubrics

Costs:
- Monthly hosting: $8
- AI grading: ~$2.50 per 100 essays
- Estimated monthly total: $30-60 for typical teacher usage

Built-in safeguards:
- Daily limits prevent cost overruns
- Real-time usage monitoring
- Automatic shutoff at monthly limits
- Teacher-friendly error messages

ROI: Teacher time savings worth significantly more than modest AI costs
```

## Frequently Asked Questions

### **Q: What if I go over the daily limit?**
**A:** The system stops processing and shows a friendly message. No additional charges. Limits reset at midnight.

### **Q: Can I increase the daily limits?**
**A:** Yes, but this requires updating the configuration. Contact your system administrator.

### **Q: What if there's an unexpected high bill?**
**A:** Set monthly limits in Anthropic console to prevent this. The system also has built-in daily limits as backup protection.

### **Q: Can multiple teachers share one account?**
**A:** Yes! The system is designed for 2-12 teachers to share costs effectively.

### **Q: How do I track spending?**
**A:** Use the `/usage/summary` endpoint or monitor via the Anthropic console dashboard.

## Support

For questions about costs or usage:
1. Check the usage dashboard: `/usage/summary`
2. Review Anthropic console: [console.anthropic.com](https://console.anthropic.com/)
3. Contact your system administrator
4. Review this guide for common scenarios

---

**Remember**: The system is designed to be cost-effective for teachers while providing significant time savings and educational value. The built-in limits ensure you won't face unexpected costs.