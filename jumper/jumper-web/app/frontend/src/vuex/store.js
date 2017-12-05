import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);


    // TODO: 放置初始状态
const state = { my_info: {} };


    // TODO: 放置我们的状态变更函数
const mutations = {
  UPDATEMYINFO (state, my_info) {
      state.my_info = my_info;
  },
};

const store=new Vuex.Store({
  state,
  mutations,
  actions: {
      updateMyInfo: ({ commit }, payload) => {
          commit('UPDATEMYINFO', payload)
      },
  },
  getters: {
      getMyInfo: state => state.my_info
  }
});

export default store
