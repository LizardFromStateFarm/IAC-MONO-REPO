#!/usr/bin/env python3
"""
Example: Programmatic Stack Creation

This example demonstrates how to create and manage Pulumi stacks programmatically
without requiring manual CLI commands.
"""

import os
import sys
from pathlib import Path

# Add the utilities directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utilities'))

from stack_manager import StackManager


def example_create_and_preview_stack():
    """Example: Create a stack and run a preview."""
    print("=== Example: Create and Preview Stack ===")
    
    # Create stack manager
    manager = StackManager()
    
    # Create or select a stack for the kind-cluster component in nonprod environment
    stack = manager.create_environment_stack(
        environment="nonprod",
        component="kind-cluster",
        config={
            "kind-cluster:environment": "nonprod"
        }
    )
    
    print(f"✅ Stack created/selected: {stack.name}")
    
    # Run a preview
    print("\n🔍 Running preview...")
    preview_output = manager.preview_stack(stack)
    print("Preview output:")
    print(preview_output)


def example_create_multiple_stacks():
    """Example: Create multiple stacks for different components."""
    print("\n=== Example: Create Multiple Stacks ===")
    
    manager = StackManager()
    
    components = ["kind-cluster", "grafana", "metrics-server"]
    environment = "nonprod"
    
    stacks = {}
    
    for component in components:
        print(f"\nCreating stack for {component}...")
        stack = manager.create_environment_stack(
            environment=environment,
            component=component,
            config={
                f"{component}:environment": environment
            }
        )
        stacks[component] = stack
        print(f"✅ Stack created for {component}: {stack.name}")
    
    return stacks


def example_deploy_stack():
    """Example: Deploy a stack."""
    print("\n=== Example: Deploy Stack ===")
    
    manager = StackManager()
    
    # Create stack
    stack = manager.create_environment_stack(
        environment="nonprod",
        component="kind-cluster"
    )
    
    print(f"✅ Stack ready: {stack.name}")
    
    # Deploy the stack
    print("\n🚀 Deploying stack...")
    deploy_output = manager.deploy_stack(stack)
    print("Deployment output:")
    print(deploy_output)


def main():
    """Run all examples."""
    print("Pulumi Stack Management Examples")
    print("=" * 50)
    
    try:
        # Example 1: Create and preview
        example_create_and_preview_stack()
        
        # Example 2: Create multiple stacks
        stacks = example_create_multiple_stacks()
        
        # Example 3: Deploy a stack (commented out to avoid actual deployment)
        # example_deploy_stack()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
