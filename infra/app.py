#!/usr/bin/env python3
import aws_cdk as cdk
from proposal_stack import ProposalDeckStack
app=cdk.App(); ProposalDeckStack(app,"ProposalDeckStack"); app.synth()
