// +build !ignore_autogenerated

/*
Copyright 2017 The Kubernetes Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// This file was autogenerated by deepcopy-gen. Do not edit it manually!

package testapigroup

import (
	v1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	conversion "k8s.io/apimachinery/pkg/conversion"
	runtime "k8s.io/apimachinery/pkg/runtime"
	reflect "reflect"
)

func init() {
	SchemeBuilder.Register(RegisterDeepCopies)
}

// RegisterDeepCopies adds deep-copy functions to the given scheme. Public
// to allow building arbitrary schemes.
func RegisterDeepCopies(scheme *runtime.Scheme) error {
	return scheme.AddGeneratedDeepCopyFuncs(
		conversion.GeneratedDeepCopyFunc{Fn: DeepCopy_testapigroup_Carp, InType: reflect.TypeOf(&Carp{})},
		conversion.GeneratedDeepCopyFunc{Fn: DeepCopy_testapigroup_CarpCondition, InType: reflect.TypeOf(&CarpCondition{})},
		conversion.GeneratedDeepCopyFunc{Fn: DeepCopy_testapigroup_CarpList, InType: reflect.TypeOf(&CarpList{})},
		conversion.GeneratedDeepCopyFunc{Fn: DeepCopy_testapigroup_CarpSpec, InType: reflect.TypeOf(&CarpSpec{})},
		conversion.GeneratedDeepCopyFunc{Fn: DeepCopy_testapigroup_CarpStatus, InType: reflect.TypeOf(&CarpStatus{})},
	)
}

// DeepCopy_testapigroup_Carp is an autogenerated deepcopy function.
func DeepCopy_testapigroup_Carp(in interface{}, out interface{}, c *conversion.Cloner) error {
	{
		in := in.(*Carp)
		out := out.(*Carp)
		*out = *in
		if newVal, err := c.DeepCopy(&in.ObjectMeta); err != nil {
			return err
		} else {
			out.ObjectMeta = *newVal.(*v1.ObjectMeta)
		}
		if newVal, err := c.DeepCopy(&in.Spec); err != nil {
			return err
		} else {
			out.Spec = *newVal.(*CarpSpec)
		}
		if newVal, err := c.DeepCopy(&in.Status); err != nil {
			return err
		} else {
			out.Status = *newVal.(*CarpStatus)
		}
		return nil
	}
}

// DeepCopy_testapigroup_CarpCondition is an autogenerated deepcopy function.
func DeepCopy_testapigroup_CarpCondition(in interface{}, out interface{}, c *conversion.Cloner) error {
	{
		in := in.(*CarpCondition)
		out := out.(*CarpCondition)
		*out = *in
		out.LastProbeTime = in.LastProbeTime.DeepCopy()
		out.LastTransitionTime = in.LastTransitionTime.DeepCopy()
		return nil
	}
}

// DeepCopy_testapigroup_CarpList is an autogenerated deepcopy function.
func DeepCopy_testapigroup_CarpList(in interface{}, out interface{}, c *conversion.Cloner) error {
	{
		in := in.(*CarpList)
		out := out.(*CarpList)
		*out = *in
		if in.Items != nil {
			in, out := &in.Items, &out.Items
			*out = make([]Carp, len(*in))
			for i := range *in {
				if newVal, err := c.DeepCopy(&(*in)[i]); err != nil {
					return err
				} else {
					(*out)[i] = *newVal.(*Carp)
				}
			}
		}
		return nil
	}
}

// DeepCopy_testapigroup_CarpSpec is an autogenerated deepcopy function.
func DeepCopy_testapigroup_CarpSpec(in interface{}, out interface{}, c *conversion.Cloner) error {
	{
		in := in.(*CarpSpec)
		out := out.(*CarpSpec)
		*out = *in
		if in.TerminationGracePeriodSeconds != nil {
			in, out := &in.TerminationGracePeriodSeconds, &out.TerminationGracePeriodSeconds
			*out = new(int64)
			**out = **in
		}
		if in.ActiveDeadlineSeconds != nil {
			in, out := &in.ActiveDeadlineSeconds, &out.ActiveDeadlineSeconds
			*out = new(int64)
			**out = **in
		}
		if in.NodeSelector != nil {
			in, out := &in.NodeSelector, &out.NodeSelector
			*out = make(map[string]string)
			for key, val := range *in {
				(*out)[key] = val
			}
		}
		return nil
	}
}

// DeepCopy_testapigroup_CarpStatus is an autogenerated deepcopy function.
func DeepCopy_testapigroup_CarpStatus(in interface{}, out interface{}, c *conversion.Cloner) error {
	{
		in := in.(*CarpStatus)
		out := out.(*CarpStatus)
		*out = *in
		if in.Conditions != nil {
			in, out := &in.Conditions, &out.Conditions
			*out = make([]CarpCondition, len(*in))
			for i := range *in {
				if newVal, err := c.DeepCopy(&(*in)[i]); err != nil {
					return err
				} else {
					(*out)[i] = *newVal.(*CarpCondition)
				}
			}
		}
		if in.StartTime != nil {
			in, out := &in.StartTime, &out.StartTime
			*out = new(v1.Time)
			**out = (*in).DeepCopy()
		}
		return nil
	}
}
